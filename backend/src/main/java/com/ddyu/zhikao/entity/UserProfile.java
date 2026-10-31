package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 考生资料，与 sys_user 一对一（user_id 唯一约束 uk_profile_user）
 */
@Data
@TableName("user_profile")
public class UserProfile {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 账号主键，唯一 */
    private Long userId;

    private String school;

    private String groupName;

    private String phone;

    private String avatar;
}
