package com.ddyu.zhikao.config;

import com.ddyu.zhikao.common.CacheKeys;
import com.ddyu.zhikao.common.LoginUser;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.UUID;

/**
 * 登录令牌的 Redis 存取：登录写入、校验续期、登出删除
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class TokenStore {

    /** 令牌有效期（秒），每次通过校验后续期 */
    private static final Duration TTL = Duration.ofSeconds(1800);

    private final StringRedisTemplate redis;
    private final ObjectMapper objectMapper;

    /** 生成令牌并缓存管理员信息 */
    public String create(LoginUser user) {
        String token = UUID.randomUUID().toString().replace("-", "");
        try {
            redis.opsForValue().set(CacheKeys.loginToken(token), objectMapper.writeValueAsString(user), TTL);
            log.info("[cache] 登录令牌写入 token={} admin={}", token, user.getUsername());
        } catch (Exception e) {
            throw new IllegalStateException("令牌写入 Redis 失败", e);
        }
        return token;
    }

    /** 读取令牌对应的管理员；命中后把 TTL 续到 30 分钟 */
    public LoginUser get(String token) {
        if (token == null || token.isBlank()) {
            return null;
        }
        String key = CacheKeys.loginToken(token);
        String json = redis.opsForValue().get(key);
        if (json == null) {
            return null;
        }
        redis.expire(key, TTL);
        try {
            return objectMapper.readValue(json, LoginUser.class);
        } catch (Exception e) {
            log.warn("令牌内容解析失败，按失效处理 token={}", token);
            return null;
        }
    }

    /** 资料修改后覆盖令牌里的用户信息，保留剩余有效期 */
    public void refresh(String token, LoginUser user) {
        if (token == null || token.isBlank()) {
            return;
        }
        String key = CacheKeys.loginToken(token);
        try {
            redis.opsForValue().setIfPresent(key, objectMapper.writeValueAsString(user), TTL);
        } catch (Exception e) {
            log.warn("令牌刷新失败 token={}", token);
        }
    }

    public void remove(String token) {
        if (token != null && !token.isBlank()) {
            redis.delete(CacheKeys.loginToken(token));
        }
    }
}
