package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 试卷内一道题 */
@Data
public class PaperQuestionVO {

    private Integer seq;
    private Integer score;
    private Long id;
    private String type;
    private String typeText;
    private String stem;
    private List<QuestionOptionVO> options;
    /** 单选/判断是字符串，多选是数组 */
    private Object answer;
    private String analysis;
    private List<TagVO> tags;

    /** XML 里接库里 JSON 原文，Service 解析后置 null */
    private String optionsJson;
    private String answerJson;
}
