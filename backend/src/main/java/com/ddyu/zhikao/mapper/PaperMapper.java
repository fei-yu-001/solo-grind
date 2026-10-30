package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.entity.ExamPaper;
import com.ddyu.zhikao.vo.PaperQuestionVO;
import com.ddyu.zhikao.vo.PaperVO;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface PaperMapper extends BaseMapper<ExamPaper> {

    /** 分页查试卷（join bank + 题目数子查询）；首参 Page 交给分页插件 */
    List<PaperVO> selectPaperPage(Page<PaperVO> page,
                                  @Param("keyword") String keyword,
                                  @Param("status") String status,
                                  @Param("bankId") Long bankId);

    /** 按主键集合取 VO */
    List<PaperVO> selectPaperByIds(@Param("ids") List<Long> ids);

    /** 试卷明细：paper_question join question，按 seq 排 */
    List<PaperQuestionVO> selectPaperQuestions(@Param("paperId") Long paperId);

    /** 多张试卷的题目明细，供分页装配 */
    List<PaperQuestionVO> selectPaperQuestionsByIds(@Param("paperIds") List<Long> paperIds);
}
