package com.ddyu.zhikao.mapper;

import com.ddyu.zhikao.vo.ExamCardVO;
import com.ddyu.zhikao.vo.ExamQuestionVO;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface ExamMapper {

    /** 考试中心：PUBLISHED 试卷 + 当前考生成绩，一条 SQL，按 id 倒序 */
    List<ExamCardVO> selectAvailablePapers(@Param("userId") Long userId);

    /** 考场题目：按题序，只取无答案的安全列 */
    List<ExamQuestionVO> selectExamQuestions(@Param("paperId") Long paperId);
}
