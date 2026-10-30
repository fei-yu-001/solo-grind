package com.ddyu.zhikao.service;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.dto.PaperForm;
import com.ddyu.zhikao.vo.PaperDetailVO;
import com.ddyu.zhikao.vo.PaperVO;

public interface PaperService {

    PageResult<PaperVO> page(String keyword, String status, Long bankId, long page, long size);

    /** 详情含题目（按题序） */
    PaperDetailVO getDetail(Long id);

    /** 组卷：随机抽题，事务 */
    PaperVO create(PaperForm form, Long operatorId);

    /** 仅 DRAFT 可改，事务 */
    PaperVO update(Long id, PaperForm form);

    void delete(Long id);

    /** DRAFT -> PUBLISHED */
    PaperVO publish(Long id);

    /** PUBLISHED -> CLOSED */
    PaperVO close(Long id);
}
