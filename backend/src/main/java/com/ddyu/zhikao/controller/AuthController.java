package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.LoginDTO;
import com.ddyu.zhikao.dto.RegisterDTO;
import com.ddyu.zhikao.service.AuthService;
import com.ddyu.zhikao.vo.LoginVO;
import com.ddyu.zhikao.vo.RegisterVO;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 认证：登录 / 登出 / 当前用户
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public Result<LoginVO> login(@Valid @RequestBody LoginDTO dto) {
        return Result.ok(authService.login(dto.getUsername(), dto.getPassword()));
    }

    /** 考生自助注册，公开接口，不发令牌 */
    @PostMapping("/register")
    public Result<RegisterVO> register(@Valid @RequestBody RegisterDTO dto) {
        return Result.ok(authService.register(dto));
    }

    @PostMapping("/logout")
    public Result<Void> logout(HttpServletRequest request) {
        authService.logout(extractToken(request));
        return Result.ok();
    }

    @GetMapping("/me")
    public Result<LoginVO> me() {
        return Result.ok(authService.me());
    }

    private String extractToken(HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            return header.substring(7).trim();
        }
        return null;
    }
}
