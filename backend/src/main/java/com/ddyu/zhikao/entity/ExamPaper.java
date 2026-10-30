package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 试卷
 */
@Data
@TableName("exam_paper")
public class ExamPaper {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String title;

    private Long bankId;

    private Integer judgeCount;

    private Integer singleCount;

    private Integer multiCount;

    private Integer judgeScore;

    private Integer singleScore;

    private Integer multiScore;

    /** 考试时长（秒） */
    private Integer durationSec;

    private Integer totalScore;

    /** DRAFT / PUBLISHED / CLOSED */
    private String status;

    private Long createdBy;

    private LocalDateTime createdAt;
}
