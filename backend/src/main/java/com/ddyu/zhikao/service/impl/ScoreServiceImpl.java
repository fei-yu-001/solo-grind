package com.ddyu.zhikao.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.common.BizException;
import com.ddyu.zhikao.common.CacheKeys;
import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.entity.Question;
import com.ddyu.zhikao.entity.QuestionBank;
import com.ddyu.zhikao.entity.SysUser;
import com.ddyu.zhikao.mapper.BankMapper;
import com.ddyu.zhikao.mapper.PaperMapper;
import com.ddyu.zhikao.mapper.QuestionMapper;
import com.ddyu.zhikao.mapper.ScoreMapper;
import com.ddyu.zhikao.mapper.UserMapper;
import com.ddyu.zhikao.service.ScoreService;
import com.ddyu.zhikao.vo.RankingVO;
import com.ddyu.zhikao.vo.ScoreDetailItemVO;
import com.ddyu.zhikao.vo.ScoreDetailVO;
import com.ddyu.zhikao.vo.ScoreVO;
import com.ddyu.zhikao.vo.StatsVO;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 成绩：分页查询、明细、撤销、统计、排行榜（Redis 300 秒）
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ScoreServiceImpl implements ScoreService {

    private static final Duration RANKING_TTL = Duration.ofSeconds(300);
    private static final Map<String, String> TYPE_TEXT = Map.of(
            "single", "单选题",
            "multi", "多选题",
            "judge", "判断题");

    private final ScoreMapper scoreMapper;
    private final BankMapper bankMapper;
    private final QuestionMapper questionMapper;
    private final PaperMapper paperMapper;
    private final UserMapper userMapper;
    private final ObjectMapper objectMapper;
    private final StringRedisTemplate redis;

    @Override
    public PageResult<ScoreVO> page(Long paperId, String keyword, long page, long size) {
        Page<ScoreVO> result = new Page<>(page, size);
        result.setRecords(scoreMapper.selectScorePage(result, paperId, keyword));
        return new PageResult<>(result.getTotal(), result.getCurrent(), result.getSize(), result.getRecords());
    }

    @Override
    public ScoreDetailVO getDetail(Long paperId, Long userId) {
        ScoreVO score = scoreMapper.selectScore(paperId, userId);
        if (score == null) {
            throw BizException.notFound("该考生没有这份试卷的成绩");
        }
        List<ScoreDetailItemVO> items = scoreMapper.selectScoreItems(paperId, userId);
        items.forEach(this::fillItem);
        ScoreDetailVO detail = new ScoreDetailVO();
        copyScoreFields(score, detail);
        detail.setItems(items);
        return detail;
    }

    /** 撤销成绩：删除该考生该试卷的全部作答记录 */
    @Transactional
    @Override
    public void delete(Long paperId, Long userId) {
        ScoreVO score = scoreMapper.selectScore(paperId, userId);
        if (score == null) {
            throw BizException.notFound("该考生没有这份试卷的成绩，无法撤销");
        }
        scoreMapper.delete(new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<com.ddyu.zhikao.entity.AnswerRecord>()
                .eq(com.ddyu.zhikao.entity.AnswerRecord::getPaperId, paperId)
                .eq(com.ddyu.zhikao.entity.AnswerRecord::getUserId, userId));
        evictRankingCache();
    }

    @Override
    public StatsVO stats() {
        StatsVO vo = new StatsVO();
        vo.setBankCount(bankMapper.selectCount(null));
        vo.setQuestionCount(questionMapper.selectCount(null));
        vo.setPaperCount(paperMapper.selectCount(null));
        vo.setUserCount(userMapper.selectCount(null));

        // 作答聚合：人数、均分、最高分、及格率
        List<ScoreVO> allScores = scoreMapper.selectScorePage(null, null, null);
        vo.setSubmittedCount((long) allScores.size());
        if (allScores.isEmpty()) {
            vo.setAvgScore(0.0);
            vo.setMaxScore(0);
            vo.setPassRate(0.0);
        } else {
            double avg = allScores.stream().mapToInt(ScoreVO::getTotalScore).average().orElse(0);
            vo.setAvgScore(Math.round(avg * 10) / 10.0);
            vo.setMaxScore(allScores.stream().mapToInt(ScoreVO::getTotalScore).max().orElse(0));
            long pass = allScores.stream().filter(s -> s.getTotalScore() >= 60).count();
            vo.setPassRate(Math.round(pass * 100.0 / allScores.size()) / 100.0);
        }

        // 按题型分组
        List<StatsVO.TypeCountVO> byType = questionMapper.selectList(null).stream()
                .collect(Collectors.groupingBy(Question::getType, Collectors.counting()))
                .entrySet().stream()
                .map(e -> {
                    StatsVO.TypeCountVO t = new StatsVO.TypeCountVO();
                    t.setTypeText(TYPE_TEXT.getOrDefault(e.getKey(), e.getKey()));
                    t.setCount(e.getValue());
                    return t;
                })
                .sorted((a, b) -> Long.compare(b.getCount(), a.getCount()))
                .toList();
        vo.setByType(byType);

        // 按题库分组
        List<StatsVO.BankCountVO> byBank = bankMapper.selectBankPage(null, null, null, null).stream()
                .map(b -> {
                    StatsVO.BankCountVO bc = new StatsVO.BankCountVO();
                    bc.setBankName(b.getName());
                    bc.setQuestionCount(b.getQuestionCount());
                    return bc;
                })
                .toList();
        vo.setByBank(byBank);
        return vo;
    }

    /** 排行榜：cache-aside，缓存 300 秒 */
    @Override
    public List<RankingVO> ranking(Long paperId, int limit) {
        String key = CacheKeys.ranking(paperId);
        try {
            String cached = redis.opsForValue().get(key);
            if (cached != null) {
                log.info("[cache] 排行榜 paperId={} 命中", paperId);
                List<RankingVO> list = objectMapper.readValue(cached, new TypeReference<List<RankingVO>>() {
                });
                return list.size() > limit ? list.subList(0, limit) : list;
            }
        } catch (Exception e) {
            log.warn("[cache] 排行榜读取失败，回源数据库: {}", e.getMessage());
        }
        log.info("[cache] 排行榜 paperId={} 未命中，回源数据库", paperId);
        List<Map<String, Object>> rows = scoreMapper.selectRanking(paperId, limit);
        List<RankingVO> list = new ArrayList<>();
        int rank = 1;
        for (Map<String, Object> row : rows) {
            Long uid = ((Number) row.get("userId")).longValue();
            String nickname = String.valueOf(row.get("nickname"));
            Integer totalScore = ((Number) row.get("totalScore")).intValue();
            list.add(new RankingVO(rank++, uid, nickname, totalScore));
        }
        try {
            redis.opsForValue().set(key, objectMapper.writeValueAsString(list), RANKING_TTL);
        } catch (Exception e) {
            log.warn("[cache] 排行榜写入失败: {}", e.getMessage());
        }
        return list;
    }

    private void fillItem(ScoreDetailItemVO item) {
        item.setTypeText(TYPE_TEXT.getOrDefault(item.getType(), item.getType()));
        item.setChosen(parseJson(item.getChosenJson()));
        item.setAnswer(parseAnswer(item.getType(), item.getAnswerJson()));
        item.setChosenJson(null);
        item.setAnswerJson(null);
    }

    private Object parseJson(String json) {
        if (json == null) {
            return null;
        }
        try {
            return objectMapper.readValue(json, Object.class);
        } catch (Exception e) {
            return json;
        }
    }

    private Object parseAnswer(String type, String json) {
        if (json == null) {
            return null;
        }
        try {
            if ("judge".equals(type)) {
                return Boolean.TRUE.equals(objectMapper.readValue(json, Boolean.class)) ? "A" : "B";
            }
            return objectMapper.readValue(json, Object.class);
        } catch (Exception e) {
            return json;
        }
    }

    private void copyScoreFields(ScoreVO from, ScoreDetailVO to) {
        to.setPaperId(from.getPaperId());
        to.setPaperTitle(from.getPaperTitle());
        to.setMaxScore(from.getMaxScore());
        to.setUserId(from.getUserId());
        to.setUsername(from.getUsername());
        to.setNickname(from.getNickname());
        to.setTotalScore(from.getTotalScore());
        to.setCorrectCount(from.getCorrectCount());
        to.setWrongCount(from.getWrongCount());
        to.setBlankCount(from.getBlankCount());
        to.setQuestionCount(from.getQuestionCount());
        to.setAccuracy(from.getAccuracy());
        to.setSubmittedAt(from.getSubmittedAt());
    }

    private void evictRankingCache() {
        try {
            java.util.Set<String> keys = redis.keys(CacheKeys.RANKING + "*");
            if (keys != null && !keys.isEmpty()) {
                redis.delete(keys);
                log.info("[cache] 撤销成绩后清除排行榜缓存 {} 个", keys.size());
            }
        } catch (Exception e) {
            log.warn("[cache] 排行榜缓存清除失败: {}", e.getMessage());
        }
    }
}
