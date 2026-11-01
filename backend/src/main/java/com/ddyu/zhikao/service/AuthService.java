package com.ddyu.zhikao.service;

import com.ddyu.zhikao.dto.RegisterDTO;
import com.ddyu.zhikao.vo.LoginVO;
import com.ddyu.zhikao.vo.RegisterVO;

public interface AuthService {

    /** 用户名密码登录，返回令牌与身份信息 */
    LoginVO login(String username, String password);

    /** 登出，删除 Redis 令牌 */
    void logout(String token);

    /** 当前登录用户信息 */
    LoginVO me();

    /** 考生自助注册，返回公开身份信息，不发令牌 */
    RegisterVO register(RegisterDTO dto);
}
