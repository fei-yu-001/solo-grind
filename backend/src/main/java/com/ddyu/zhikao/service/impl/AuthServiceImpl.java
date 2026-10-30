package com.ddyu.zhikao.service.impl;

import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.LoginContext;
import com.ddyu.zhikao.common.LoginUser;
import com.ddyu.zhikao.config.TokenStore;
import com.ddyu.zhikao.entity.SysUser;
import com.ddyu.zhikao.mapper.UserMapper;
import com.ddyu.zhikao.service.AuthService;
import com.ddyu.zhikao.vo.LoginVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * 认证：登录发令牌、登出删令牌、取当前用户
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserMapper userMapper;
    private final TokenStore tokenStore;
    private final PasswordEncoder passwordEncoder;

    @Override
    public LoginVO login(String username, String password) {
        SysUser user = userMapper.selectByUsername(username);
        if (user == null || !passwordEncoder.matches(password, user.getPassword())) {
            throw BizException.unauthorized("用户名或密码错误");
        }
        if (user.getStatus() != null && user.getStatus() == 0) {
            throw BizException.unauthorized("账号已停用");
        }
        String token = tokenStore.create(new LoginUser(user.getId(), user.getUsername(),
                user.getNickname(), user.getRole()));
        log.info("用户登录 username={} role={}", username, user.getRole());
        LoginVO vo = new LoginVO();
        vo.setToken(token);
        vo.setId(user.getId());
        vo.setUsername(user.getUsername());
        vo.setNickname(user.getNickname());
        vo.setRole(user.getRole());
        return vo;
    }

    @Override
    public void logout(String token) {
        tokenStore.remove(token);
    }

    @Override
    public LoginVO me() {
        LoginUser user = LoginContext.get();
        LoginVO vo = new LoginVO();
        vo.setId(user.getId());
        vo.setUsername(user.getUsername());
        vo.setNickname(user.getNickname());
        vo.setRole(user.getRole());
        return vo;
    }
}
