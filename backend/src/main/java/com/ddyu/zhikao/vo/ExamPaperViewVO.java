package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 考场试卷视图：试卷信息 + 无答案的题目列表 */
@Data
public class ExamPaperViewVO {

    private Long paperId;
    private String title;
    private Integer durationSec;
    private Integer totalScore;
    private Integer questionCount;

    private List<ExamQuestionVO> questions;
}
