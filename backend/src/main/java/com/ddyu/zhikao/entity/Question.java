package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 题目，options 与 answer 在库里是 JSON 字符串，序列化在 Service 做
 */
@Data
@TableName("question")
public class Question {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bankId;

    /** single 单选 / multi 多选 / judge 判断 */
    private String type;

    private String stem;

    /** JSON 字符串，如 [{"key":"A","text":"..."}]，判断题为 true/false */
    private String options;

    /** JSON 字符串，单选 "B"、多选 ["A","C"]、判断 true/false */
    private String answer;

    private String analysis;

    /** 1 易 / 2 中 / 3 难 */
    private Integer difficulty;

    private Integer sortNo;

    private LocalDateTime createdAt;
}
