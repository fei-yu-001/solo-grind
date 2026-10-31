package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ddyu.zhikao.entity.UserProfile;
import com.ddyu.zhikao.vo.ProfileVO;
import org.apache.ibatis.annotations.Param;

public interface UserProfileMapper extends BaseMapper<UserProfile> {

    /** 一对一关联查询：账号 LEFT JOIN 资料，一个账号最多一行资料 */
    ProfileVO selectProfileByUserId(@Param("userId") Long userId);
}
