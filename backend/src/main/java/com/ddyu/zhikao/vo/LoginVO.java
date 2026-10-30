package com.ddyu.zhikao.vo;

import lombok.Data;

/** 登录出参 */
@Data
public class LoginVO {

    private String token;
    private Long id;
    private String username;
    private String nickname;
    private String role;
}
