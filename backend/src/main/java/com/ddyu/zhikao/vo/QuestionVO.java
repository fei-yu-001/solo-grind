package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 题目出参 */
@Data
public class QuestionVO {

    private Long id;
    private Long bankId;
    private String bankName;
    private String type;
    private String typeText;
    private String stem;
    private List<QuestionOptionVO> options;
    /** 单选/判断是字符串，多选是数组 */
    private Object answer;
    private String analysis;
    private Integer difficulty;
    private String difficultyText;
    private Integer sortNo;
    private List<TagVO> tags;
    private String createdAt;

    /** XML 里接库里 JSON 原文，Service 解析后置 null */
    private String optionsJson;
    private String answerJson;
}
