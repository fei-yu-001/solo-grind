package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 题库
 */
@Data
@TableName("question_bank")
public class QuestionBank {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;

    /** 本科组 / 专科组 */
    private String groupName;

    private String description;

    /** ENABLED / DISABLED */
    private String status;

    private LocalDateTime createdAt;
}
