package com.ddyu.zhikao.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.ddyu.zhikao.entity.Tag;
import com.ddyu.zhikao.vo.TagVO;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface TagMapper extends BaseMapper<Tag> {

    /** 标签列表带题目数（子查询计数，不 join） */
    List<TagVO> selectTagList(@Param("questionIds") List<Long> questionIds);
}
