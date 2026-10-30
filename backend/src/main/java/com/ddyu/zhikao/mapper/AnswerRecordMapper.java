package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ddyu.zhikao.entity.AnswerRecord;
import com.ddyu.zhikao.vo.ScoreVO;
import org.apache.ibatis.annotations.Param;

public interface AnswerRecordMapper extends BaseMapper<AnswerRecord> {

    /** 某考生某试卷的聚合成绩 */
    ScoreVO selectScore(@Param("paperId") Long paperId, @Param("userId") Long userId);
}
