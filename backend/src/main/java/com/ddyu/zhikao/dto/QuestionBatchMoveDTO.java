package com.ddyu.zhikao.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

/** 批量移动题目到题库 */
@Data
public class QuestionBatchMoveDTO {

    @NotEmpty(message = "题目 id 不能为空")
    private List<Long> ids;

    @NotNull(message = "目标题库不能为空")
    private Long bankId;
}
