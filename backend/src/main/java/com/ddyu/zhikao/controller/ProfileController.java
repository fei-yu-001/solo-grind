package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.ProfileForm;
import com.ddyu.zhikao.service.ProfileService;
import com.ddyu.zhikao.vo.ProfileVO;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 个人资料：管理员和考生都能看、改自己的
 */
@RestController
@RequestMapping("/api/profile")
@RequiredArgsConstructor
public class ProfileController {

    private final ProfileService profileService;

    @GetMapping
    public Result<ProfileVO> mine() {
        return Result.ok(profileService.mine());
    }

    @PutMapping
    public Result<ProfileVO> update(@Valid @RequestBody ProfileForm form, HttpServletRequest request) {
        String header = request.getHeader("Authorization");
        String token = header != null && header.startsWith("Bearer ") ? header.substring(7).trim() : null;
        return Result.ok(profileService.update(form, token));
    }
}
