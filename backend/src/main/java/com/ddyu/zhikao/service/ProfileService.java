package com.ddyu.zhikao.service;

import com.ddyu.zhikao.dto.ProfileForm;
import com.ddyu.zhikao.vo.ProfileVO;

public interface ProfileService {

    /** 当前登录人的资料（一对一关联查询） */
    ProfileVO mine();

    /** 修改昵称和资料：同时写 sys_user 和 user_profile，事务 */
    ProfileVO update(ProfileForm form, String token);
}
