package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.entity.Question;
import com.ddyu.zhikao.vo.QuestionVO;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface QuestionMapper extends BaseMapper<Question> {

    /** 分页查题目（question join question_bank，条件多；一对多的标签不在这里 join）；首参 Page 交给分页插件 */
    List<QuestionVO> selectQuestionPage(Page<QuestionVO> page,
                                        @Param("bankId") Long bankId,
                                        @Param("type") String type,
                                        @Param("keyword") String keyword,
                                        @Param("difficulty") Integer difficulty,
                                        @Param("tagId") Long tagId);

    /** 按主键集合批量取 VO，供 Service 装配标签 */
    List<QuestionVO> selectQuestionByIds(@Param("ids") List<Long> ids);

    /** 题库内按题型随机抽 n 道题的主键 */
    List<Long> selectRandomIds(@Param("bankId") Long bankId,
                               @Param("type") String type,
                               @Param("limit") int limit);
}
