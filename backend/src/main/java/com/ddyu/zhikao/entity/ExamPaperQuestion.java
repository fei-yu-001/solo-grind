package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 试卷-题目关联，带题序与分值，无自增主键
 */
@Data
@TableName("exam_paper_question")
public class ExamPaperQuestion {

    private Long paperId;

    private Long questionId;

    /** 题序，从 1 开始 */
    private Integer seq;

    /** 本题分值 */
    private Integer score;
}
