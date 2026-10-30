package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 登录账号，管理员和考生共用一张表，用 role 区分
 */
@Data
@TableName("sys_user")
public class SysUser {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String username;

    /** BCrypt 哈希 */
    private String password;

    private String nickname;

    /** ADMIN / STUDENT */
    private String role;

    /** 1 启用 0 停用 */
    private Integer status;

    private LocalDateTime createdAt;
}
