package com.ddyu.zhikao.vo;

import lombok.Data;

/** 成绩明细里的一道题 */
@Data
public class ScoreDetailItemVO {

    private Integer seq;
    private Long questionId;
    private String type;
    private String typeText;
    private String stem;
    /** 单选/判断是字符串，多选是数组；未答为 null */
    private Object chosen;
    private Object answer;
    private Integer correct;
    private Integer score;

    /** XML 里接库里 JSON 原文，Service 解析后置 null */
    private String chosenJson;
    private String answerJson;
}
