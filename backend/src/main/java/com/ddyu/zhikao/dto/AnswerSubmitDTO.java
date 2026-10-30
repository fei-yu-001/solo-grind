package com.ddyu.zhikao.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

/** 交卷入参 */
@Data
public class AnswerSubmitDTO {

    @NotNull(message = "试卷 id 不能为空")
    private Long paperId;

    @NotEmpty(message = "作答不能为空")
    @Valid
    private List<AnswerItemDTO> answers;

    @Data
    public static class AnswerItemDTO {
        @NotNull(message = "题目 id 不能为空")
        private Long questionId;
        /** 单选/判断传字符串，多选传数组，未答不传或传 null */
        private Object chosen;
    }
}
