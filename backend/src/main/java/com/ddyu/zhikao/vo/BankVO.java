package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 题库出参 */
@Data
public class BankVO {

    private Long id;
    private String name;
    private String groupName;
    private String description;
    private String status;
    private String statusText;
    private Long questionCount;
    private String createdAt;

    private List<TagVO> tags;
}
