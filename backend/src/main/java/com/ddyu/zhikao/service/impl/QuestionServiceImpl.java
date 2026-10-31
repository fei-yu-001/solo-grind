package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.dto.QuestionBatchMoveDTO;
import com.ddyu.zhikao.dto.QuestionForm;
import com.ddyu.zhikao.entity.ExamPaperQuestion;
import com.ddyu.zhikao.entity.Question;
import com.ddyu.zhikao.entity.QuestionTag;
import com.ddyu.zhikao.entity.Tag;
import com.ddyu.zhikao.mapper.ExamPaperQuestionMapper;
import com.ddyu.zhikao.mapper.QuestionMapper;
import com.ddyu.zhikao.mapper.QuestionTagMapper;
import com.ddyu.zhikao.mapper.TagMapper;
import com.ddyu.zhikao.service.AdminGuardService;
import com.ddyu.zhikao.service.QuestionService;
import com.ddyu.zhikao.service.word.DocxQuestionParser;
import com.ddyu.zhikao.service.word.DocxTextExtractor;
import com.ddyu.zhikao.vo.QuestionImportErrorVO;
import com.ddyu.zhikao.vo.QuestionImportVO;
import com.ddyu.zhikao.vo.QuestionVO;
import com.ddyu.zhikao.vo.TagVO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * 题目：分页条件查询、增删改、批量移动、标签装配
 */
@Service
@RequiredArgsConstructor
public class QuestionServiceImpl implements QuestionService {

    private static final Map<String, String> TYPE_TEXT = Map.of(
            "single", "单选题",
            "multi", "多选题",
            "judge", "判断题");
    private static final Map<Integer, String> DIFFICULTY_TEXT = Map.of(
            1, "易", 2, "中", 3, "难");
    private static final int IMPORT_ERROR_LIMIT = 20;

    private final DocxQuestionParser docxQuestionParser = new DocxQuestionParser();

    private final QuestionMapper questionMapper;
    private final QuestionTagMapper questionTagMapper;
    private final ExamPaperQuestionMapper examPaperQuestionMapper;
    private final TagMapper tagMapper;
    private final AdminGuardService adminGuardService;
    private final ObjectMapper objectMapper;

    @Override
    public PageResult<QuestionVO> page(Long bankId, String type, String keyword, Integer difficulty, Long tagId,
                                       long page, long size) {
        Page<QuestionVO> result = new Page<>(page, size);
        result.setRecords(questionMapper.selectQuestionPage(result, bankId, type, keyword, difficulty, tagId));
        fillTypeAndDifficulty(result.getRecords());
        fillTags(result.getRecords());
        return new PageResult<>(result.getTotal(), result.getCurrent(), result.getSize(), result.getRecords());
    }

    @Override
    public QuestionVO getById(Long id) {
        QuestionVO vo = questionMapper.selectQuestionByIds(List.of(id)).stream().findFirst()
                .orElseThrow(() -> BizException.notFound("题目不存在"));
        fillTypeAndDifficulty(List.of(vo));
        fillTags(List.of(vo));
        return vo;
    }

    @Transactional
    @Override
    public QuestionVO create(QuestionForm form) {
        adminGuardService.checkBankExists(form.getBankId());
        validateAnswer(form.getType(), form.getAnswer());
        Question question = new Question();
        applyForm(question, form);
        questionMapper.insert(question);
        saveTags(question.getId(), form.getTagIds());
        return getById(question.getId());
    }

    @Transactional
    @Override
    public QuestionVO update(Long id, QuestionForm form) {
        Question question = questionMapper.selectById(id);
        if (question == null) {
            throw BizException.notFound("题目不存在");
        }
        adminGuardService.checkBankExists(form.getBankId());
        validateAnswer(form.getType(), form.getAnswer());
        applyForm(question, form);
        questionMapper.updateById(question);
        questionTagMapper.delete(new LambdaQueryWrapper<QuestionTag>().eq(QuestionTag::getQuestionId, id));
        saveTags(id, form.getTagIds());
        return getById(id);
    }

    /** 被试卷引用时不能删 */
    @Transactional
    @Override
    public void delete(Long id) {
        Question question = questionMapper.selectById(id);
        if (question == null) {
            throw BizException.notFound("题目不存在");
        }
        Long used = examPaperQuestionMapper.selectCount(
                new LambdaQueryWrapper<ExamPaperQuestion>().eq(ExamPaperQuestion::getQuestionId, id));
        if (used > 0) {
            throw BizException.conflict("题目被 " + used + " 张试卷引用，不能删除");
        }
        questionTagMapper.delete(new LambdaQueryWrapper<QuestionTag>().eq(QuestionTag::getQuestionId, id));
        questionMapper.deleteById(id);
    }

    /** 批量移动题目到题库 */
    @Transactional
    @Override
    public int batchMove(QuestionBatchMoveDTO dto) {
        adminGuardService.checkBankExists(dto.getBankId());
        List<Long> distinctIds = dto.getIds().stream().distinct().toList();
        List<Question> questions = questionMapper.selectBatchIds(distinctIds);
        if (questions.size() < distinctIds.size()) {
            throw BizException.badRequest("有题目不存在，无法移动");
        }
        questions.forEach(q -> q.setBankId(dto.getBankId()));
        questions.forEach(questionMapper::updateById);
        return questions.size();
    }

    /** 全部校验通过才入库；有任何一道不合法就整批回滚 */
    @Transactional
    @Override
    public QuestionImportVO importDocx(MultipartFile file, Long bankId, Integer difficulty) {
        if (bankId == null) {
            throw BizException.badRequest("题库不能为空");
        }
        int level = difficulty == null ? 1 : difficulty;
        if (level < 1 || level > 3) {
            throw BizException.badRequest("难度只能是 1~3");
        }
        adminGuardService.checkBankExists(bankId);
        DocxQuestionParser.ParseResult parsed = docxQuestionParser.parse(DocxTextExtractor.paragraphs(file));
        if (!parsed.getErrors().isEmpty() || parsed.getQuestions().isEmpty()) {
            throw importRejected(parsed);
        }
        for (DocxQuestionParser.ParsedQuestion item : parsed.getQuestions()) {
            questionMapper.insert(toQuestion(item, bankId, level));
        }
        QuestionImportVO vo = new QuestionImportVO();
        vo.setImported(parsed.getQuestions().size());
        vo.setSkipped(0);
        vo.setErrors(List.of());
        return vo;
    }

    private BizException importRejected(DocxQuestionParser.ParseResult parsed) {
        List<QuestionImportErrorVO> errors = new ArrayList<>();
        for (DocxQuestionParser.ParseError error : parsed.getErrors()) {
            if (errors.size() >= IMPORT_ERROR_LIMIT) {
                break;
            }
            errors.add(new QuestionImportErrorVO(error.getLine(), error.getReason()));
        }
        QuestionImportVO data = new QuestionImportVO();
        data.setImported(0);
        data.setSkipped(0);
        data.setErrors(errors);
        // 空文档或整篇对不上格式：固定这句；已经认出题目但有不合法的，用第一处原因
        boolean noQuestion = parsed.getQuestions().isEmpty();
        String message = noQuestion
                ? "没有解析到题目，请检查文档格式"
                : errors.get(0).getReason();
        return BizException.badRequest(message, data);
    }

    private Question toQuestion(DocxQuestionParser.ParsedQuestion item, Long bankId, int difficulty) {
        Question question = new Question();
        question.setBankId(bankId);
        question.setType(item.getType());
        question.setStem(item.getStem());
        question.setOptions(toImportOptionsJson(item.getOptions()));
        question.setAnswer(toImportAnswerJson(item.getType(), item.getAnswerLetters()));
        question.setAnalysis(null);
        question.setDifficulty(difficulty);
        question.setSortNo(item.getSortNo());
        return question;
    }

    private String toImportOptionsJson(Map<String, String> options) {
        List<Map<String, String>> list = new ArrayList<>();
        options.forEach((key, text) -> {
            Map<String, String> option = new LinkedHashMap<>();
            option.put("key", key);
            option.put("text", text);
            list.add(option);
        });
        try {
            return objectMapper.writeValueAsString(list);
        } catch (Exception e) {
            throw new IllegalStateException("选项序列化失败", e);
        }
    }

    private String toImportAnswerJson(String type, String letters) {
        try {
            if ("multi".equals(type)) {
                List<String> answer = new ArrayList<>();
                for (char letter : letters.toCharArray()) {
                    answer.add(String.valueOf(letter));
                }
                return objectMapper.writeValueAsString(answer);
            }
            return objectMapper.writeValueAsString(letters);
        } catch (Exception e) {
            throw new IllegalStateException("答案序列化失败", e);
        }
    }

    private void applyForm(Question question, QuestionForm form) {
        question.setBankId(form.getBankId());
        question.setType(form.getType());
        question.setStem(form.getStem());
        question.setOptions(toOptionsJson(form));
        question.setAnswer(toAnswerJson(form.getType(), form.getAnswer()));
        question.setAnalysis(form.getAnalysis());
        question.setDifficulty(form.getDifficulty());
        question.setSortNo(form.getSortNo() == null ? 0 : form.getSortNo());
    }

    private void saveTags(Long questionId, List<Long> tagIds) {
        if (tagIds == null || tagIds.isEmpty()) {
            return;
        }
        for (Long tagId : new LinkedHashSet<>(tagIds)) {
            adminGuardService.checkTagExists(tagId);
            QuestionTag qt = new QuestionTag();
            qt.setQuestionId(questionId);
            qt.setTagId(tagId);
            questionTagMapper.insert(qt);
        }
    }

    /** 按题型校验答案形态：单选/判断字符串，多选非空数组 */
    private void validateAnswer(String type, Object answer) {
        switch (type) {
            case "multi" -> {
                if (!(answer instanceof List<?> list) || list.isEmpty()) {
                    throw BizException.badRequest("多选题答案必须是非空数组，如 [\"A\",\"C\"]");
                }
            }
            case "single" -> {
                if (!(answer instanceof String s) || s.isBlank()) {
                    throw BizException.badRequest("单选题答案必须是选项字母，如 \"B\"");
                }
            }
            case "judge" -> {
                String s = answer instanceof String text ? text : null;
                if (!"A".equals(s) && !"B".equals(s)) {
                    throw BizException.badRequest("判断题答案必须是 \"A\"（对）或 \"B\"（错）");
                }
            }
            default -> throw BizException.badRequest("题型不合法：" + type);
        }
    }

    private String toOptionsJson(QuestionForm form) {
        try {
            if ("judge".equals(form.getType())) {
                // 判断题选项：前端传了就用前端的，没传默认 A 对 / B 错
                List<QuestionForm.QuestionOptionForm> options = form.getOptions();
                if (options == null || options.isEmpty()) {
                    return objectMapper.writeValueAsString(List.of(
                            judgeOption("A", "对"), judgeOption("B", "错")));
                }
                return objectMapper.writeValueAsString(options);
            }
            return objectMapper.writeValueAsString(form.getOptions());
        } catch (Exception e) {
            throw new IllegalStateException("选项序列化失败", e);
        }
    }

    private QuestionForm.QuestionOptionForm judgeOption(String key, String text) {
        QuestionForm.QuestionOptionForm option = new QuestionForm.QuestionOptionForm();
        option.setKey(key);
        option.setText(text);
        return option;
    }

    private String toAnswerJson(String type, Object answer) {
        try {
            // 判断题和单选一样存 JSON 字符串 "A"/"B"（契约 4.3）
            return objectMapper.writeValueAsString(answer);
        } catch (Exception e) {
            throw new IllegalStateException("答案序列化失败", e);
        }
    }

    private void fillTypeAndDifficulty(List<QuestionVO> list) {
        list.forEach(vo -> {
            vo.setTypeText(TYPE_TEXT.get(vo.getType()));
            vo.setDifficultyText(DIFFICULTY_TEXT.get(vo.getDifficulty()));
            vo.setOptions(parseOptions(vo.getOptionsJson()));
            vo.setAnswer(parseAnswer(vo.getType(), vo.getAnswerJson()));
            vo.setOptionsJson(null);
            vo.setAnswerJson(null);
        });
    }

    /** 标签二次 IN 查询，Service 装配，不在分页 SQL 里 join */
    private void fillTags(List<QuestionVO> list) {
        if (list.isEmpty()) {
            return;
        }
        List<Long> questionIds = list.stream().map(QuestionVO::getId).toList();
        List<QuestionTag> relations = questionTagMapper.selectList(
                new LambdaQueryWrapper<QuestionTag>().in(QuestionTag::getQuestionId, questionIds));
        if (relations.isEmpty()) {
            list.forEach(vo -> vo.setTags(List.of()));
            return;
        }
        Set<Long> tagIds = relations.stream().map(QuestionTag::getTagId).collect(Collectors.toCollection(LinkedHashSet::new));
        Map<Long, Tag> tagMap = tagMapper.selectBatchIds(tagIds).stream()
                .collect(Collectors.toMap(Tag::getId, Function.identity()));
        Map<Long, List<QuestionTag>> byQuestion = relations.stream()
                .collect(Collectors.groupingBy(QuestionTag::getQuestionId));
        for (QuestionVO vo : list) {
            vo.setTags(byQuestion.getOrDefault(vo.getId(), List.of()).stream()
                    .map(r -> {
                        TagVO tagVO = new TagVO();
                        tagVO.setId(r.getTagId());
                        Tag tag = tagMap.get(r.getTagId());
                        if (tag != null) {
                            tagVO.setName(tag.getName());
                            tagVO.setColor(tag.getColor());
                        }
                        return tagVO;
                    })
                    .toList());
        }
    }

    private List<com.ddyu.zhikao.vo.QuestionOptionVO> parseOptions(String json) {
        if (json == null || json.isBlank()) {
            return List.of();
        }
        try {
            // 兼容历史布尔存法 [true, false]，转成 A 对 / B 错
            if (json.contains("true") || json.contains("false")) {
                return List.of(optionVO("A", "对"), optionVO("B", "错"));
            }
            return objectMapper.readValue(json,
                    new TypeReference<List<com.ddyu.zhikao.vo.QuestionOptionVO>>() {
                    });
        } catch (Exception e) {
            return List.of();
        }
    }

    private com.ddyu.zhikao.vo.QuestionOptionVO optionVO(String key, String text) {
        com.ddyu.zhikao.vo.QuestionOptionVO vo = new com.ddyu.zhikao.vo.QuestionOptionVO();
        vo.setKey(key);
        vo.setText(text);
        return vo;
    }

    private Object parseAnswer(String type, String json) {
        if (json == null) {
            return null;
        }
        try {
            if ("judge".equals(type)) {
                // 判断题答案存 JSON 字符串 "A"/"B"；历史布尔 true/false 读失败时映射成 A/B
                try {
                    return objectMapper.readValue(json, String.class);
                } catch (Exception ignored) {
                    return Boolean.TRUE.equals(objectMapper.readValue(json, Boolean.class)) ? "A" : "B";
                }
            }
            if ("multi".equals(type)) {
                return objectMapper.readValue(json, new TypeReference<List<String>>() {
                });
            }
            return objectMapper.readValue(json, String.class);
        } catch (Exception e) {
            return json;
        }
    }
}
