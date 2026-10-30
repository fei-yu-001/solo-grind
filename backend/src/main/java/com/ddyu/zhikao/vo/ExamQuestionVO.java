package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/**
 * 考场用题目视图：防作弊，绝不携带 answer / analysis，
 * 不复用 QuestionVO，SQL 层就不查这两个字段
 */
@Data
public class ExamQuestionVO {

    private Integer seq;
    private Long questionId;
    private String type;
    private String typeText;
    private String stem;
    private List<QuestionOptionVO> options;
    private Integer score;

    /** XML 里接库里 JSON 原文，Service 解析后置 null；仅作中转，不序列化 */
    @com.fasterxml.jackson.annotation.JsonIgnore
    private String optionsJson;
}
