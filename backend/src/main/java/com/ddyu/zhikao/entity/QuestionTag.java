package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 题目-标签多对多关联，无自增主键
 */
@Data
@TableName("question_tag")
public class QuestionTag {

    private Long questionId;

    private Long tagId;
}
