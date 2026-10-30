package com.ddyu.zhikao.service;

import com.ddyu.zhikao.common.LoginUser;

/**
 * 管理权限与引用存在性校验
 */
public interface AdminGuardService {

    /** 非 ADMIN 抛 403 */
    void checkAdmin();

    /** LoginContext 里的当前用户 */
    LoginUser currentUser();

    /** 题库存在性校验 */
    void checkBankExists(Long bankId);

    /** 标签存在性校验 */
    void checkTagExists(Long tagId);
}
