package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.dto.PaperForm;
import com.ddyu.zhikao.entity.ExamPaper;
import com.ddyu.zhikao.entity.ExamPaperQuestion;
import com.ddyu.zhikao.entity.Question;
import com.ddyu.zhikao.mapper.ExamPaperQuestionMapper;
import com.ddyu.zhikao.mapper.PaperMapper;
import com.ddyu.zhikao.mapper.QuestionMapper;
import com.ddyu.zhikao.service.PaperService;
import com.ddyu.zhikao.vo.PaperDetailVO;
import com.ddyu.zhikao.vo.PaperQuestionVO;
import com.ddyu.zhikao.vo.PaperVO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 试卷：分页条件查询、详情（含题）、组卷、状态流转
 */
@Service
@RequiredArgsConstructor
public class PaperServiceImpl implements PaperService {

    private static final Map<String, String> STATUS_TEXT = Map.of(
            "DRAFT", "草稿",
            "PUBLISHED", "已发布",
            "CLOSED", "已结束");
    private static final Map<String, String> TYPE_TEXT = Map.of(
            "single", "单选题",
            "multi", "多选题",
            "judge", "判断题");

    private final PaperMapper paperMapper;
    private final ExamPaperQuestionMapper examPaperQuestionMapper;
    private final QuestionMapper questionMapper;
    private final ObjectMapper objectMapper;

    @Override
    public PageResult<PaperVO> page(String keyword, String status, Long bankId, long page, long size) {
        Page<PaperVO> result = new Page<>(page, size);
        result.setRecords(paperMapper.selectPaperPage(result, keyword, status, bankId));
        fillStatusText(result.getRecords());
        return new PageResult<>(result.getTotal(), result.getCurrent(), result.getSize(), result.getRecords());
    }

    @Override
    public PaperDetailVO getDetail(Long id) {
        PaperVO paper = paperMapper.selectPaperByIds(List.of(id)).stream().findFirst()
                .orElseThrow(() -> BizException.notFound("试卷不存在"));
        paper.setStatusText(STATUS_TEXT.getOrDefault(paper.getStatus(), paper.getStatus()));
        List<PaperQuestionVO> questions = paperMapper.selectPaperQuestions(id);
        questions.forEach(this::fillQuestion);
        PaperDetailVO detail = new PaperDetailVO();
        copyPaperFields(paper, detail);
        detail.setQuestions(questions);
        return detail;
    }

    /**
     * 组卷：按题型从题库随机抽题，事务写 exam_paper + 批量写 exam_paper_question。
     * 题序：判断题在前、单选中、多选后，题序内随机。
     */
    @Transactional
    @Override
    public PaperVO create(PaperForm form, Long operatorId) {
        int judgeCount = form.getJudgeCount();
        int singleCount = form.getSingleCount();
        int multiCount = form.getMultiCount();
        if (judgeCount + singleCount + multiCount == 0) {
            throw BizException.badRequest("三种题型加起来至少要 1 道题");
        }

        List<Long> judgeIds = draw(form.getBankId(), "judge", judgeCount);
        List<Long> singleIds = draw(form.getBankId(), "single", singleCount);
        List<Long> multiIds = draw(form.getBankId(), "multi", multiCount);

        ExamPaper paper = new ExamPaper();
        paper.setTitle(form.getTitle());
        paper.setBankId(form.getBankId());
        paper.setJudgeCount(judgeCount);
        paper.setSingleCount(singleCount);
        paper.setMultiCount(multiCount);
        paper.setJudgeScore(form.getJudgeScore());
        paper.setSingleScore(form.getSingleScore());
        paper.setMultiScore(form.getMultiScore());
        paper.setDurationSec(form.getDurationSec());
        int totalScore = judgeCount * form.getJudgeScore()
                + singleCount * form.getSingleScore()
                + multiCount * form.getMultiScore();
        paper.setTotalScore(totalScore);
        paper.setStatus("DRAFT");
        paper.setCreatedBy(operatorId);
        paperMapper.insert(paper);

        int seq = 1;
        List<ExamPaperQuestion> relations = new ArrayList<>();
        for (Long qid : judgeIds) {
            relations.add(paperQuestion(paper.getId(), qid, seq++, form.getJudgeScore()));
        }
        for (Long qid : singleIds) {
            relations.add(paperQuestion(paper.getId(), qid, seq++, form.getSingleScore()));
        }
        for (Long qid : multiIds) {
            relations.add(paperQuestion(paper.getId(), qid, seq++, form.getMultiScore()));
        }
        relations.forEach(examPaperQuestionMapper::insert);

        return paperMapper.selectPaperByIds(List.of(paper.getId())).stream().findFirst()
                .map(vo -> {
                    vo.setStatusText(STATUS_TEXT.getOrDefault(vo.getStatus(), vo.getStatus()));
                    return vo;
                })
                .orElseThrow(() -> new IllegalStateException("组卷后查不到试卷"));
    }

    /** 仅 DRAFT 可改组卷，重新抽题 */
    @Transactional
    @Override
    public PaperVO update(Long id, PaperForm form) {
        ExamPaper paper = paperMapper.selectById(id);
        if (paper == null) {
            throw BizException.notFound("试卷不存在");
        }
        if (!"DRAFT".equals(paper.getStatus())) {
            throw BizException.conflict("只有草稿状态的试卷才能修改组卷，当前状态是 "
                    + STATUS_TEXT.getOrDefault(paper.getStatus(), paper.getStatus()));
        }
        if (form.getJudgeCount() + form.getSingleCount() + form.getMultiCount() == 0) {
            throw BizException.badRequest("三种题型加起来至少要 1 道题");
        }
        // 重新抽题
        examPaperQuestionMapper.delete(new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<ExamPaperQuestion>()
                .eq(ExamPaperQuestion::getPaperId, id));
        int seq = 1;
        for (Long qid : draw(form.getBankId(), "judge", form.getJudgeCount())) {
            examPaperQuestionMapper.insert(paperQuestion(id, qid, seq++, form.getJudgeScore()));
        }
        for (Long qid : draw(form.getBankId(), "single", form.getSingleCount())) {
            examPaperQuestionMapper.insert(paperQuestion(id, qid, seq++, form.getSingleScore()));
        }
        for (Long qid : draw(form.getBankId(), "multi", form.getMultiCount())) {
            examPaperQuestionMapper.insert(paperQuestion(id, qid, seq++, form.getMultiScore()));
        }
        paper.setTitle(form.getTitle());
        paper.setBankId(form.getBankId());
        paper.setJudgeCount(form.getJudgeCount());
        paper.setSingleCount(form.getSingleCount());
        paper.setMultiCount(form.getMultiCount());
        paper.setJudgeScore(form.getJudgeScore());
        paper.setSingleScore(form.getSingleScore());
        paper.setMultiScore(form.getMultiScore());
        paper.setDurationSec(form.getDurationSec());
        paper.setTotalScore(form.getJudgeCount() * form.getJudgeScore()
                + form.getSingleCount() * form.getSingleScore()
                + form.getMultiCount() * form.getMultiScore());
        paperMapper.updateById(paper);
        return paperMapper.selectPaperByIds(List.of(id)).stream().findFirst()
                .map(vo -> {
                    vo.setStatusText(STATUS_TEXT.getOrDefault(vo.getStatus(), vo.getStatus()));
                    return vo;
                })
                .orElseThrow(() -> new IllegalStateException("改卷后查不到试卷"));
    }

    @Transactional
    @Override
    public void delete(Long id) {
        ExamPaper paper = paperMapper.selectById(id);
        if (paper == null) {
            throw BizException.notFound("试卷不存在");
        }
        // exam_paper_question 对 paper 有 ON DELETE CASCADE，这里显式删更直观
        examPaperQuestionMapper.delete(new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<ExamPaperQuestion>()
                .eq(ExamPaperQuestion::getPaperId, id));
        paperMapper.deleteById(id);
    }

    /** DRAFT -> PUBLISHED */
    @Transactional
    @Override
    public PaperVO publish(Long id) {
        ExamPaper paper = paperMapper.selectById(id);
        if (paper == null) {
            throw BizException.notFound("试卷不存在");
        }
        if (!"DRAFT".equals(paper.getStatus())) {
            throw BizException.conflict("只有草稿试卷才能发布，当前状态是 "
                    + STATUS_TEXT.getOrDefault(paper.getStatus(), paper.getStatus()));
        }
        paper.setStatus("PUBLISHED");
        paperMapper.updateById(paper);
        return paperMapper.selectPaperByIds(List.of(id)).stream().findFirst()
                .map(vo -> {
                    vo.setStatusText(STATUS_TEXT.getOrDefault(vo.getStatus(), vo.getStatus()));
                    return vo;
                })
                .orElseThrow(() -> new IllegalStateException("发布后查不到试卷"));
    }

    /** PUBLISHED -> CLOSED */
    @Transactional
    @Override
    public PaperVO close(Long id) {
        ExamPaper paper = paperMapper.selectById(id);
        if (paper == null) {
            throw BizException.notFound("试卷不存在");
        }
        if (!"PUBLISHED".equals(paper.getStatus())) {
            throw BizException.conflict("只有已发布的试卷才能结束，当前状态是 "
                    + STATUS_TEXT.getOrDefault(paper.getStatus(), paper.getStatus()));
        }
        paper.setStatus("CLOSED");
        paperMapper.updateById(paper);
        return paperMapper.selectPaperByIds(List.of(id)).stream().findFirst()
                .map(vo -> {
                    vo.setStatusText(STATUS_TEXT.getOrDefault(vo.getStatus(), vo.getStatus()));
                    return vo;
                })
                .orElseThrow(() -> new IllegalStateException("结束后查不到试卷"));
    }

    private ExamPaperQuestion paperQuestion(Long paperId, Long questionId, int seq, int score) {
        ExamPaperQuestion pq = new ExamPaperQuestion();
        pq.setPaperId(paperId);
        pq.setQuestionId(questionId);
        pq.setSeq(seq);
        pq.setScore(score);
        return pq;
    }

    /** 题量不足时报业务冲突，文案带上题型和余量 */
    private List<Long> draw(Long bankId, String type, int count) {
        if (count == 0) {
            return List.of();
        }
        List<Long> ids = questionMapper.selectRandomIds(bankId, type, count);
        if (ids.size() < count) {
            throw BizException.conflict("题库里" + TYPE_TEXT.get(type) + "只剩 " + ids.size()
                    + " 道，组不出来 " + count + " 道");
        }
        return ids;
    }

    private void fillQuestion(PaperQuestionVO vo) {
        vo.setTypeText(TYPE_TEXT.getOrDefault(vo.getType(), vo.getType()));
        vo.setOptions(parseOptions(vo.getOptionsJson()));
        vo.setAnswer(parseAnswer(vo.getType(), vo.getAnswerJson()));
        vo.setOptionsJson(null);
        vo.setAnswerJson(null);
        vo.setTags(List.of());
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

    private void fillStatusText(List<PaperVO> list) {
        list.forEach(vo -> vo.setStatusText(STATUS_TEXT.getOrDefault(vo.getStatus(), vo.getStatus())));
    }

    private void copyPaperFields(PaperVO from, PaperDetailVO to) {
        to.setId(from.getId());
        to.setTitle(from.getTitle());
        to.setBankId(from.getBankId());
        to.setBankName(from.getBankName());
        to.setJudgeCount(from.getJudgeCount());
        to.setSingleCount(from.getSingleCount());
        to.setMultiCount(from.getMultiCount());
        to.setJudgeScore(from.getJudgeScore());
        to.setSingleScore(from.getSingleScore());
        to.setMultiScore(from.getMultiScore());
        to.setDurationSec(from.getDurationSec());
        to.setTotalScore(from.getTotalScore());
        to.setQuestionCount(from.getQuestionCount());
        to.setStatus(from.getStatus());
        to.setStatusText(from.getStatusText());
        to.setCreatedAt(from.getCreatedAt());
    }
}
