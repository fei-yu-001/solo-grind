package com.ddyu.zhikao.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/** 组卷入参，后端按题型从题库随机抽题 */
@Data
public class PaperForm {

    @NotBlank(message = "试卷名不能为空")
    private String title;

    @NotNull(message = "来源题库不能为空")
    private Long bankId;

    @NotNull(message = "判断题数量不能为空")
    @Min(value = 0, message = "题量不能为负数")
    private Integer judgeCount;

    @NotNull(message = "单选题数量不能为空")
    @Min(value = 0, message = "题量不能为负数")
    private Integer singleCount;

    @NotNull(message = "多选题数量不能为空")
    @Min(value = 0, message = "题量不能为负数")
    private Integer multiCount;

    @NotNull(message = "判断题分值不能为空")
    @Min(value = 1, message = "分值至少 1 分")
    private Integer judgeScore;

    @NotNull(message = "单选题分值不能为空")
    @Min(value = 1, message = "分值至少 1 分")
    private Integer singleScore;

    @NotNull(message = "多选题分值不能为空")
    @Min(value = 1, message = "分值至少 1 分")
    private Integer multiScore;

    @NotNull(message = "考试时长不能为空")
    @Min(value = 60, message = "考试时长至少 60 秒")
    @Max(value = 14400, message = "考试时长不能超过 4 小时")
    private Integer durationSec;
}
