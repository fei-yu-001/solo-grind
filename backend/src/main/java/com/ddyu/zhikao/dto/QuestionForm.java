package com.ddyu.zhikao.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

import java.util.List;

/** 题目新增/修改入参 */
@Data
public class QuestionForm {

    @NotNull(message = "所属题库不能为空")
    private Long bankId;

    @NotBlank(message = "题型不能为空")
    @Pattern(regexp = "single|multi|judge", message = "题型只能是 single、multi、judge")
    private String type;

    @NotBlank(message = "题干不能为空")
    private String stem;

    @NotNull(message = "选项不能为空")
    @Valid
    private List<QuestionOptionForm> options;

    /** 单选/判断传字符串，多选传数组，Service 按题型校验 */
    @NotNull(message = "答案不能为空")
    private Object answer;

    private String analysis;

    @NotNull(message = "难度不能为空")
    @Min(value = 1, message = "难度只能是 1~3")
    @Max(value = 3, message = "难度只能是 1~3")
    private Integer difficulty;

    private Integer sortNo;

    private List<Long> tagIds;

    @Data
    public static class QuestionOptionForm {
        @NotBlank(message = "选项 key 不能为空")
        private String key;
        @NotBlank(message = "选项内容不能为空")
        private String text;
    }
}
