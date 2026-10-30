package com.ddyu.zhikao.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/** 标签新增入参 */
@Data
public class TagForm {

    @NotBlank(message = "标签名不能为空")
    private String name;

    private String color;
}
