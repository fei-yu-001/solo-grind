package com.ddyu.zhikao.vo;

import lombok.Data;

/** 成绩出参（列表行） */
@Data
public class ScoreVO {

    private Long paperId;
    private String paperTitle;
    private Integer maxScore;
    private Long userId;
    private String username;
    private String nickname;
    private Integer totalScore;
    private Integer correctCount;
    private Integer wrongCount;
    private Integer blankCount;
    private Integer questionCount;
    private Double accuracy;
    private String submittedAt;
}
