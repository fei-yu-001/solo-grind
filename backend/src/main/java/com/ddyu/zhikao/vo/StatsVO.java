package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.List;

/** 首页统计 */
@Data
public class StatsVO {

    private Long bankCount;
    private Long questionCount;
    private Long paperCount;
    private Long userCount;
    private Long submittedCount;
    private Double avgScore;
    private Integer maxScore;
    private Double passRate;
    private List<TypeCountVO> byType;
    private List<BankCountVO> byBank;

    @Data
    public static class TypeCountVO {
        private String typeText;
        private Long count;
    }

    @Data
    public static class BankCountVO {
        private String bankName;
        private Long questionCount;
    }
}
