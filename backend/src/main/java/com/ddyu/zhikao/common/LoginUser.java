package com.ddyu.zhikao.common;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 登录后缓存在 Redis 里的用户信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LoginUser {

    private Long id;
    private String username;
    private String nickname;
    /** ADMIN / STUDENT */
    private String role;
}
