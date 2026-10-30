package com.ddyu.zhikao.service;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.dto.BankForm;
import com.ddyu.zhikao.vo.BankVO;

public interface BankService {

    /** 分页 + 条件查询 */
    PageResult<BankVO> page(String keyword, String groupName, String status, long page, long size);

    /** 全部题库，走 Redis 字典缓存 */
    java.util.List<BankVO> listAll();

    BankVO getById(Long id);

    BankVO create(BankForm form);

    BankVO update(Long id, BankForm form);

    /** 题库下还有题目时 409 */
    void delete(Long id);
}
