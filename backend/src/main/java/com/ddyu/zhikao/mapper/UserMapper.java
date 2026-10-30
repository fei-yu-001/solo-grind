package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ddyu.zhikao.entity.SysUser;
import org.apache.ibatis.annotations.Param;

public interface UserMapper extends BaseMapper<SysUser> {

    /** 登录：按用户名取账号 */
    SysUser selectByUsername(@Param("username") String username);
}
