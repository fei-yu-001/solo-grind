package com.ddyu.zhikao.common;

/**
 * Redis key 统一在这里拼，避免各处手写字符串写错
 */
public final class CacheKeys {

    /** 登录令牌 */
    public static final String LOGIN_TOKEN = "login:token:";
    /** 分类字典 */
    public static final String DICT_CATEGORIES = "dict:categories";
    /** 热门图书前缀，后面拼 limit */
    public static final String HOT_BOOKS = "cache:hot:books:";
    /** 空值标记，用于防缓存穿透 */
    public static final String EMPTY_VALUE = "__EMPTY__";

    private CacheKeys() {
    }

    public static String loginToken(String token) {
        return LOGIN_TOKEN + token;
    }

    public static String hotBooks(int limit) {
        return HOT_BOOKS + limit;
    }
}
