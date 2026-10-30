package com.ddyu.zhikao.service;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.vo.RankingVO;
import com.ddyu.zhikao.vo.ScoreDetailVO;
import com.ddyu.zhikao.vo.ScoreVO;
import com.ddyu.zhikao.vo.StatsVO;

import java.util.List;

public interface ScoreService {

    PageResult<ScoreVO> page(Long paperId, String keyword, long page, long size);

    /** 成绩明细（逐题） */
    ScoreDetailVO getDetail(Long paperId, Long userId);

    /** 撤销成绩，事务 */
    void delete(Long paperId, Long userId);

    /** 首页统计 */
    StatsVO stats();

    /** 排行榜，Redis 缓存 300 秒 */
    List<RankingVO> ranking(Long paperId, int limit);
}
