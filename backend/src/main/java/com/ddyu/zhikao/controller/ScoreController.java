package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.service.AdminGuardService;
import com.ddyu.zhikao.service.ScoreService;
import com.ddyu.zhikao.vo.RankingVO;
import com.ddyu.zhikao.vo.ScoreDetailVO;
import com.ddyu.zhikao.vo.ScoreVO;
import com.ddyu.zhikao.vo.StatsVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 成绩查询 / 明细 / 撤销 / 统计 / 排行榜
 */
@RestController
@RequestMapping("/api/scores")
@RequiredArgsConstructor
public class ScoreController {

    private final ScoreService scoreService;
    private final AdminGuardService adminGuardService;

    @GetMapping
    public Result<PageResult<ScoreVO>> page(@RequestParam(required = false) Long paperId,
                                            @RequestParam(required = false) String keyword,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "10") long size) {
        return Result.ok(scoreService.page(paperId, keyword, page, size));
    }

    @GetMapping("/stats")
    public Result<StatsVO> stats() {
        return Result.ok(scoreService.stats());
    }

    @GetMapping("/ranking")
    public Result<List<RankingVO>> ranking(@RequestParam Long paperId,
                                           @RequestParam(defaultValue = "10") int limit) {
        return Result.ok(scoreService.ranking(paperId, limit));
    }

    @GetMapping("/{paperId}/{userId}")
    public Result<ScoreDetailVO> detail(@PathVariable Long paperId, @PathVariable Long userId) {
        return Result.ok(scoreService.getDetail(paperId, userId));
    }

    /** 撤销成绩 */
    @DeleteMapping("/{paperId}/{userId}")
    public Result<Void> delete(@PathVariable Long paperId, @PathVariable Long userId) {
        adminGuardService.checkAdmin();
        scoreService.delete(paperId, userId);
        return Result.ok();
    }
}
