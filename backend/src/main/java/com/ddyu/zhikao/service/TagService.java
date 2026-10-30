package com.ddyu.zhikao.service;

import com.ddyu.zhikao.dto.TagForm;
import com.ddyu.zhikao.vo.TagVO;

import java.util.List;

public interface TagService {

    List<TagVO> list();

    TagVO create(TagForm form);

    void delete(Long id);
}
