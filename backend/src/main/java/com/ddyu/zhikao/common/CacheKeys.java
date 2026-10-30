package com.ddyu.zhikao.common;

/**
 * Redis key 统一在这里拼，避免各处手写字符串写错
 */
public final class CacheKeys {

    /** 登录令牌 */
    public static final String LOGIN_TOKEN = "login:token:";
    /** 题库字典 */
    public static final String DICT_BANKS = "dict:banks";
    /** 成绩排行榜前缀，后面拼 paperId */
    public static final String RANKING = "cache:ranking:";
    /** 空值标记，用于防缓存穿透 */
    public static final String EMPTY_VALUE = "__EMPTY__";

    private CacheKeys() {
    }

    public static String loginToken(String token) {
        return LOGIN_TOKEN + token;
    }

    public static String ranking(Long paperId) {
        return RANKING + paperId;
    }
}
