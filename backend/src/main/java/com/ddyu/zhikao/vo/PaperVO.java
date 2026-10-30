package com.ddyu.zhikao.vo;

import lombok.Data;

/** 试卷出参 */
@Data
public class PaperVO {

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
}
