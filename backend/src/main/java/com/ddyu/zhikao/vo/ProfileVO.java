package com.ddyu.zhikao.vo;

import lombok.Data;

/** 个人资料：账号信息 + 一对一的资料 */
@Data
public class ProfileVO {

    private Long userId;
    private String username;
    private String nickname;
    private String role;

    /** 没填过资料时为 null */
    private Detail profile;

    @Data
    public static class Detail {
        private Long id;
        private String school;
        private String groupName;
        private String phone;
    }
}
