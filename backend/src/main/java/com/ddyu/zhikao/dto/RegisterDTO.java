package com.ddyu.zhikao.dto;

import jakarta.validation.GroupSequence;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 考生注册入参。
 * 先校验必填，全部通过后再校验格式，保证空值时只返回「请输入…」而不是两条错误。
 */
@Data
@GroupSequence({RegisterDTO.class, RegisterDTO.Format.class})
public class RegisterDTO {

    /** 第二组：格式与长度 */
    public interface Format {
    }

    @NotBlank(message = "请输入用户名")
    @Pattern(regexp = "^[A-Za-z0-9_]{4,20}$", message = "用户名需为 4-20 位字母、数字或下划线", groups = Format.class)
    private String username;

    @NotBlank(message = "请输入密码")
    @Size(min = 6, max = 20, message = "密码长度需为 6-20 位", groups = Format.class)
    private String password;

    @NotBlank(message = "请输入昵称")
    @Size(max = 16, message = "昵称最多 16 个字", groups = Format.class)
    private String nickname;
}