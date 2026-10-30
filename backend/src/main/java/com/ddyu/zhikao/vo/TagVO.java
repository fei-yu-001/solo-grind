package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 标签出参 */
@Data
public class TagVO {

    private Long id;
    private String name;
    private String color;
    private Long questionCount;
}
