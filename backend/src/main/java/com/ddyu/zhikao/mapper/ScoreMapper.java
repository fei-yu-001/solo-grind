package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.entity.AnswerRecord;
import com.ddyu.zhikao.vo.ScoreDetailItemVO;
import com.ddyu.zhikao.vo.ScoreVO;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

public interface ScoreMapper extends BaseMapper<AnswerRecord> {

    /** 成绩分页：answer_record join sys_user join exam_paper，按 paper+user 分组聚合；首参 Page 交给分页插件；userId 非空时只查该考生 */
    List<ScoreVO> selectScorePage(Page<ScoreVO> page,
                                  @Param("paperId") Long paperId,
                                  @Param("keyword") String keyword,
                                  @Param("userId") Long userId);

    /** 某考生某试卷的聚合成绩 */
    ScoreVO selectScore(@Param("paperId") Long paperId, @Param("userId") Long userId);

    /** 逐题明细：answer_record join exam_paper_question join question */
    List<ScoreDetailItemVO> selectScoreItems(@Param("paperId") Long paperId,
                                             @Param("userId") Long userId);

    /** 排行榜：按总分倒序 */
    List<Map<String, Object>> selectRanking(@Param("paperId") Long paperId,
                                            @Param("limit") int limit);

    /** 首页统计的作答聚合块 */
    Map<String, Object> selectScoreStats();
}
