package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.LoginContext;
import com.ddyu.zhikao.common.LoginUser;
import com.ddyu.zhikao.entity.QuestionBank;
import com.ddyu.zhikao.entity.Tag;
import com.ddyu.zhikao.mapper.BankMapper;
import com.ddyu.zhikao.mapper.TagMapper;
import com.ddyu.zhikao.service.AdminGuardService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

/**
 * 管理权限守卫与引用存在性校验
 */
@Service
@RequiredArgsConstructor
public class AdminGuardServiceImpl implements AdminGuardService {

    private final BankMapper bankMapper;
    private final TagMapper tagMapper;

    @Override
    public void checkAdmin() {
        LoginUser user = LoginContext.get();
        if (user == null || !"ADMIN".equals(user.getRole())) {
            throw new BizException(403, "没有权限，该操作仅管理员可用");
        }
    }

    @Override
    public LoginUser currentUser() {
        return LoginContext.get();
    }

    @Override
    public void checkBankExists(Long bankId) {
        if (bankMapper.selectById(bankId) == null) {
            throw BizException.notFound("题库不存在");
        }
    }

    @Override
    public void checkTagExists(Long tagId) {
        if (tagMapper.selectCount(new LambdaQueryWrapper<Tag>().eq(Tag::getId, tagId)) == 0) {
            throw BizException.badRequest("标签不存在：" + tagId);
        }
    }
}
