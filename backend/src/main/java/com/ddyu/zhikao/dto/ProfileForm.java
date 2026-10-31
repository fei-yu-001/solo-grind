package com.ddyu.zhikao.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/** 修改个人资料入参 */
@Data
public class ProfileForm {

    @NotBlank(message = "昵称不能为空")
    @Size(max = 32, message = "昵称不能超过 32 个字符")
    private String nickname;

    @Size(max = 64, message = "学校不能超过 64 个字符")
    private String school;

    @Size(max = 16, message = "组别不能超过 16 个字符")
    private String groupName;

    @Pattern(regexp = "^$|^1[0-9]{10}$", message = "手机号必须是 11 位数字")
    private String phone;
}
