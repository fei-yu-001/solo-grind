package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.LoginContext;
import com.ddyu.zhikao.common.LoginUser;
import com.ddyu.zhikao.config.TokenStore;
import com.ddyu.zhikao.dto.ProfileForm;
import com.ddyu.zhikao.entity.SysUser;
import com.ddyu.zhikao.entity.UserProfile;
import com.ddyu.zhikao.mapper.UserMapper;
import com.ddyu.zhikao.mapper.UserProfileMapper;
import com.ddyu.zhikao.service.ProfileService;
import com.ddyu.zhikao.vo.ProfileVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 个人资料：sys_user 与 user_profile 一对一
 */
@Service
@RequiredArgsConstructor
public class ProfileServiceImpl implements ProfileService {

    private final UserMapper userMapper;
    private final UserProfileMapper userProfileMapper;
    private final TokenStore tokenStore;

    @Override
    public ProfileVO mine() {
        ProfileVO vo = userProfileMapper.selectProfileByUserId(LoginContext.get().getId());
        if (vo == null) {
            throw BizException.notFound("账号不存在");
        }
        if (vo.getProfile() != null && vo.getProfile().getId() == null) {
            vo.setProfile(null);
        }
        return vo;
    }

    /** 两张表一起改，任何一步失败整体回滚；资料不存在就新建，保证一对一 */
    @Transactional
    @Override
    public ProfileVO update(ProfileForm form, String token) {
        LoginUser login = LoginContext.get();
        SysUser user = userMapper.selectById(login.getId());
        if (user == null) {
            throw BizException.notFound("账号不存在");
        }
        user.setNickname(form.getNickname().trim());
        userMapper.updateById(user);

        UserProfile profile = userProfileMapper.selectOne(
                new LambdaQueryWrapper<UserProfile>().eq(UserProfile::getUserId, login.getId()));
        boolean created = profile == null;
        if (created) {
            profile = new UserProfile();
            profile.setUserId(login.getId());
        }
        profile.setSchool(blankToNull(form.getSchool()));
        profile.setGroupName(blankToNull(form.getGroupName()));
        profile.setPhone(blankToNull(form.getPhone()));
        if (created) {
            userProfileMapper.insert(profile);
        } else {
            userProfileMapper.updateById(profile);
        }

        // 令牌里缓存了昵称，改完同步刷新
        tokenStore.refresh(token,
                new LoginUser(login.getId(), login.getUsername(), user.getNickname(), login.getRole()));
        return mine();
    }

    private String blankToNull(String s) {
        return s == null || s.isBlank() ? null : s.trim();
    }
}
