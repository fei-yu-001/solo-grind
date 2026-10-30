package com.ddyu.zhikao;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 图书借阅管理后台启动类
 */
@SpringBootApplication
@MapperScan("com.ddyu.zhikao.mapper")
public class ZhikaoApplication {

    public static void main(String[] args) {
        SpringApplication.run(ZhikaoApplication.class, args);
    }
}
