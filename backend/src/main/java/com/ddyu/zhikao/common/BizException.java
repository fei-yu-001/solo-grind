package com.ddyu.zhikao.common;

import lombok.Getter;

/**
 * 业务异常，由全局异常处理器转成对应状态码
 */
@Getter
public class BizException extends RuntimeException {

    private final int code;

    /** 业务失败时仍要带给前端的附加数据，例如导入错误明细；没有则为 null */
    private final Object data;

    public BizException(int code, String message) {
        this(code, message, null);
    }

    public BizException(int code, String message, Object data) {
        super(message);
        this.code = code;
        this.data = data;
    }

    public static BizException badRequest(String message) {
        return new BizException(400, message);
    }

    public static BizException badRequest(String message, Object data) {
        return new BizException(400, message, data);
    }

    public static BizException unauthorized(String message) {
        return new BizException(401, message);
    }

    public static BizException notFound(String message) {
        return new BizException(404, message);
    }

    public static BizException conflict(String message) {
        return new BizException(409, message);
    }
}
