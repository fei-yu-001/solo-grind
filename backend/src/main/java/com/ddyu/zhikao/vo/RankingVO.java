package com.ddyu.zhikao.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/** 排行榜一行 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RankingVO {

    private Integer rank;
    private Long userId;
    private String nickname;
    private Integer totalScore;
}
