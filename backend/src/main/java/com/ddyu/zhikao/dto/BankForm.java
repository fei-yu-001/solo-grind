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

    @NotBlank(message = "组别不能为空")
    @Pattern(regexp = "本科组|专科组", message = "组别只能是本科组或专科组")
    private String groupName;

    @Size(max = 255, message = "题库说明不能超过 255 个字符")
    private String description;

    @Pattern(regexp = "ENABLED|DISABLED", message = "状态只能是 ENABLED 或 DISABLED")
    private String status;
}
