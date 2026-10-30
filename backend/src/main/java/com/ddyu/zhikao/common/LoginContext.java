package com.ddyu.zhikao.common;

/**
 * 当前请求的登录上下文，由拦截器写入，Controller/Service 只读
 */
public final class LoginContext {

    private static final ThreadLocal<LoginUser> HOLDER = new ThreadLocal<>();

    private LoginContext() {
    }

    public static void set(LoginUser user) {
        HOLDER.set(user);
    }

    public static LoginUser get() {
        return HOLDER.get();
    }

    public static Long currentAdminId() {
        LoginUser user = HOLDER.get();
        return user == null ? null : user.getId();
    }

    public static void clear() {
        HOLDER.remove();
    }
}
