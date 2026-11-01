package com.ddyu.zhikao.vo;

import lombok.Data;

/** 注册成功返回，只有公开身份信息，不含密码 */
@Data
public class RegisterVO {

    private Long id;
    private String username;
    private String nickname;
    private String role;
}