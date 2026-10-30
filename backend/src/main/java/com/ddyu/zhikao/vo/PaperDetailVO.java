package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 试卷详情 = PaperVO + 题目列表 */
@Data
public class PaperDetailVO {

    private Long id;
    private String title;
    private Long bankId;
    private String bankName;
    private Integer judgeCount;
    private Integer singleCount;
    private Integer multiCount;
    private Integer judgeScore;
    private Integer singleScore;
    private Integer multiScore;
    private Integer durationSec;
    private Integer totalScore;
    private Long questionCount;
    private String status;
    private String statusText;
    private String createdAt;

    private List<PaperQuestionVO> questions;
}
