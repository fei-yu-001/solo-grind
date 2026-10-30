package com.ddyu.zhikao.vo;

import lombok.Data;

/** 考试中心卡片：已发布试卷 + 当前考生的作答状态 */
@Data
public class ExamCardVO {

    private Long paperId;
    private String title;
    private String bankName;
    private Long questionCount;
    private Integer totalScore;
    private Integer durationSec;
    /** 当前考生的得分，没交过为 null */
    private Integer myScore;
    /** 当前考生的交卷时间，没交过为 null */
    private String mySubmittedAt;
}
