package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.ddyu.zhikao.entity.QuestionBank;
import com.ddyu.zhikao.vo.BankVO;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface BankMapper extends BaseMapper<QuestionBank> {

    /** 分页查题库（主表 + 题目数子查询，不 join 一对多）；首参 Page 交给分页插件 */
    List<BankVO> selectBankPage(Page<BankVO> page,
                                @Param("keyword") String keyword,
                                @Param("groupName") String groupName,
                                @Param("status") String status);

    /** 按主键集合取 VO（题目数子查询） */
    List<BankVO> selectBankByIds(@Param("ids") List<Long> ids);
}
