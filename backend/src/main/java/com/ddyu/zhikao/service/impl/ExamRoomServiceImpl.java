package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.entity.AnswerRecord;
import com.ddyu.zhikao.entity.ExamPaper;
import com.ddyu.zhikao.mapper.AnswerRecordMapper;
import com.ddyu.zhikao.mapper.ExamMapper;
import com.ddyu.zhikao.mapper.PaperMapper;
import com.ddyu.zhikao.service.ExamRoomService;
import com.ddyu.zhikao.vo.ExamCardVO;
import com.ddyu.zhikao.vo.ExamPaperViewVO;
import com.ddyu.zhikao.vo.ExamQuestionVO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * 考生在线答题：考试中心、进考场。题目视图不带 answer / analysis
 */
@Service
@RequiredArgsConstructor
public class ExamRoomServiceImpl implements ExamRoomService {

    private static final Map<String, String> TYPE_TEXT = Map.of(
            "single", "单选题",
            "multi", "多选题",
            "judge", "判断题");

    private final ExamMapper examMapper;
    private final PaperMapper paperMapper;
    private final AnswerRecordMapper answerRecordMapper;
    private final ObjectMapper objectMapper;

    @Override
    public List<ExamCardVO> available(Long userId) {
        return examMapper.selectAvailablePapers(userId);
    }

    @Override
    public ExamPaperViewVO getExamView(Long paperId, Long userId) {
        ExamPaper paper = paperMapper.selectById(paperId);
        if (paper == null) {
            throw BizException.notFound("试卷不存在");
        }
        if (!"PUBLISHED".equals(paper.getStatus())) {
            throw BizException.conflict("试卷未发布或已结束，不能进入考试");
        }
        Long submitted = answerRecordMapper.selectCount(
                new LambdaQueryWrapper<AnswerRecord>()
                        .eq(AnswerRecord::getPaperId, paperId)
                        .eq(AnswerRecord::getUserId, userId));
        if (submitted > 0) {
            throw BizException.conflict("你已经交过这份试卷了");
        }
        List<ExamQuestionVO> questions = examMapper.selectExamQuestions(paperId);
        questions.forEach(this::fillQuestion);
        ExamPaperViewVO vo = new ExamPaperViewVO();
        vo.setPaperId(paper.getId());
        vo.setTitle(paper.getTitle());
        vo.setDurationSec(paper.getDurationSec());
        vo.setTotalScore(paper.getTotalScore());
        vo.setQuestionCount(questions.size());
        vo.setQuestions(questions);
        return vo;
    }

    private void fillQuestion(ExamQuestionVO vo) {
        vo.setTypeText(TYPE_TEXT.getOrDefault(vo.getType(), vo.getType()));
        vo.setOptions(parseOptions(vo.getOptionsJson()));
        vo.setOptionsJson(null);
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
}
