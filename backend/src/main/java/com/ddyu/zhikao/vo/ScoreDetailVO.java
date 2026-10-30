package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 成绩明细 = ScoreVO + 逐题明细 */
@Data
public class ScoreDetailVO {

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

    private List<ScoreDetailItemVO> items;
}
