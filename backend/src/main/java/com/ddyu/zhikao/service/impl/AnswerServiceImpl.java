package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.CacheKeys;
import com.ddyu.zhikao.dto.AnswerSubmitDTO;
import com.ddyu.zhikao.entity.AnswerRecord;
import com.ddyu.zhikao.entity.ExamPaper;
import com.ddyu.zhikao.entity.ExamPaperQuestion;
import com.ddyu.zhikao.entity.Question;
import com.ddyu.zhikao.mapper.AnswerRecordMapper;
import com.ddyu.zhikao.mapper.ExamPaperMapper;
import com.ddyu.zhikao.mapper.ExamPaperQuestionMapper;
import com.ddyu.zhikao.mapper.QuestionMapper;
import com.ddyu.zhikao.mapper.ScoreMapper;
import com.ddyu.zhikao.service.AnswerService;
import com.ddyu.zhikao.vo.ScoreVO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * 交卷判分：契约 4.7 的判分规则都写在这里，Controller 不算分
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AnswerServiceImpl implements AnswerService {

    private static final Map<String, String> TYPE_TEXT = Map.of(
            "single", "单选题",
            "multi", "多选题",
            "judge", "判断题");

    private final ExamPaperMapper paperMapper;
    private final ExamPaperQuestionMapper examPaperQuestionMapper;
    private final QuestionMapper questionMapper;
    private final AnswerRecordMapper answerRecordMapper;
    private final ScoreMapper scoreMapper;
    private final ObjectMapper objectMapper;
    private final StringRedisTemplate redis;

    /**
     * 交卷：批量写 answer_record，事务。同一考生同一试卷只能交一次。
     */
    @Transactional
    @Override
    public ScoreVO submit(AnswerSubmitDTO dto, Long userId) {
        ExamPaper paper = paperMapper.selectById(dto.getPaperId());
        if (paper == null) {
            throw BizException.notFound("试卷不存在");
        }
        if (!"PUBLISHED".equals(paper.getStatus())) {
            throw BizException.conflict("试卷未发布或已结束，不能交卷，当前状态是 " + paper.getStatus());
        }
        Long submitted = answerRecordMapper.selectCount(
                new LambdaQueryWrapper<AnswerRecord>()
                        .eq(AnswerRecord::getPaperId, dto.getPaperId())
                        .eq(AnswerRecord::getUserId, userId));
        if (submitted > 0) {
            throw BizException.conflict("同一考生同一试卷只能交一次卷");
        }

        // 试卷全部题目与分值，未答的也要落库（chosen 为 null，计入 blankCount）
        Map<Long, ExamPaperQuestion> paperQuestions = examPaperQuestionMapper.selectList(
                        new LambdaQueryWrapper<ExamPaperQuestion>()
                                .eq(ExamPaperQuestion::getPaperId, dto.getPaperId()))
                .stream()
                .collect(Collectors.toMap(ExamPaperQuestion::getQuestionId, Function.identity()));
        if (paperQuestions.isEmpty()) {
            throw BizException.conflict("试卷没有题目，不能交卷");
        }

        // 作答里的题目必须都在卷子里
        Set<Long> answeredIds = dto.getAnswers().stream()
                .map(AnswerSubmitDTO.AnswerItemDTO::getQuestionId)
                .collect(Collectors.toSet());
        List<Long> notInPaper = answeredIds.stream()
                .filter(qid -> !paperQuestions.containsKey(qid))
                .toList();
        if (!notInPaper.isEmpty()) {
            throw BizException.badRequest("作答包含不属于该试卷的题目 " + notInPaper.get(0));
        }

        // 取标准答案
        Map<Long, Question> questionMap = questionMapper.selectBatchIds(paperQuestions.keySet()).stream()
                .collect(Collectors.toMap(Question::getId, Function.identity()));

        LocalDateTime now = LocalDateTime.now();
        Map<Long, AnswerSubmitDTO.AnswerItemDTO> answerByQuestion = dto.getAnswers().stream()
                .collect(Collectors.toMap(AnswerSubmitDTO.AnswerItemDTO::getQuestionId, Function.identity(), (a, b) -> a));
        List<AnswerRecord> records = paperQuestions.values().stream()
                .map(pq -> {
                    Question question = questionMap.get(pq.getQuestionId());
                    AnswerSubmitDTO.AnswerItemDTO item = answerByQuestion.get(pq.getQuestionId());
                    Object chosen = item == null ? null : item.getChosen();
                    int score = grade(question.getType(), question.getAnswer(), chosen, pq.getScore());
                    AnswerRecord record = new AnswerRecord();
                    record.setPaperId(dto.getPaperId());
                    record.setUserId(userId);
                    record.setQuestionId(pq.getQuestionId());
                    record.setChosen(toChosenJson(chosen));
                    record.setCorrect(score == pq.getScore() ? 1 : 0);
                    record.setScore(score);
                    record.setSubmittedAt(now);
                    return record;
                })
                .toList();
        records.forEach(answerRecordMapper::insert);

        // 排行榜缓存失效
        evictRankingCache();

        return scoreMapperScoreVO(dto.getPaperId(), userId);
    }

    /**
     * 判分规则（契约 4.7）：
     * 单选/判断：与标准答案完全一致得满分，否则 0 分
     * 多选：全对得满分；少选（真子集）得一半分（向下取整）；多选或错选 0 分
     * 未作答：0 分
     */
    int grade(String type, String answerJson, Object chosen, int fullScore) {
        if (chosen == null) {
            return 0;
        }
        try {
            switch (type) {
                case "single", "judge" -> {
                    String expected;
                    if ("judge".equals(type)) {
                        // 判断题答案存 JSON 字符串 "A"/"B"；历史布尔 true/false 兼容映射成 A/B
                        try {
                            expected = objectMapper.readValue(answerJson, String.class);
                        } catch (Exception ignored) {
                            expected = Boolean.TRUE.equals(objectMapper.readValue(answerJson, Boolean.class)) ? "A" : "B";
                        }
                    } else {
                        expected = objectMapper.readValue(answerJson, String.class);
                    }
                    return expected.equals(String.valueOf(chosen)) ? fullScore : 0;
                }
                case "multi" -> {
                    List<String> expected = objectMapper.readValue(answerJson, new TypeReference<List<String>>() {
                    });
                    if (!(chosen instanceof List<?> chosenList)) {
                        return 0;
                    }
                    Set<String> chosenSet = chosenList.stream()
                            .map(String::valueOf)
                            .collect(Collectors.toSet());
                    if (chosenSet.size() > expected.size()) {
                        return 0;
                    }
                    boolean allCorrect = chosenSet.stream().allMatch(expected::contains);
                    if (!allCorrect) {
                        return 0;
                    }
                    if (chosenSet.size() == expected.size()) {
                        return fullScore;
                    }
                    // 少选：真子集得一半分，向下取整
                    return (int) Math.floor(fullScore / 2.0);
                }
                default -> {
                    return 0;
                }
            }
        } catch (BizException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalStateException("答案解析失败", e);
        }
    }

    private String toChosenJson(Object chosen) {
        if (chosen == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(chosen);
        } catch (Exception e) {
            throw new IllegalStateException("作答序列化失败", e);
        }
    }

    /** 交卷后重新查聚合成绩返回 */
    private ScoreVO scoreMapperScoreVO(Long paperId, Long userId) {
        ScoreVO vo = scoreMapper.selectScore(paperId, userId);
        if (vo == null) {
            throw new IllegalStateException("交卷后查不到成绩");
        }
        return vo;
    }

    private void evictRankingCache() {
        try {
            Set<String> keys = redis.keys(CacheKeys.RANKING + "*");
            if (keys != null && !keys.isEmpty()) {
                redis.delete(keys);
                log.info("[cache] 交卷后清除排行榜缓存 {} 个", keys.size());
            }
        } catch (Exception e) {
            log.warn("[cache] 排行榜缓存清除失败: {}", e.getMessage());
        }
    }
}
