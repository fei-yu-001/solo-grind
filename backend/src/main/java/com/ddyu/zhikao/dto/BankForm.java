package com.ddyu.zhikao.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/** 题库新增/修改入参 */
@Data
public class BankForm {

    @NotBlank(message = "题库名不能为空")
    @Size(max = 64, message = "题库名不能超过 64 个字符")
    private String name;

    @Size(max = 16, message = "组别不能超过 16 个字符")
    private String groupName;

    @Size(max = 255, message = "题库说明不能超过 255 个字符")
    private String description;

    @Pattern(regexp = "ENABLED|DISABLED", message = "状态只能是 ENABLED 或 DISABLED")
    private String status;
}
