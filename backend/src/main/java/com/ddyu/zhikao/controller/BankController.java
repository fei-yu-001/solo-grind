package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.BankForm;
import com.ddyu.zhikao.service.AdminGuardService;
import com.ddyu.zhikao.service.BankService;
import com.ddyu.zhikao.vo.BankVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 题库管理：增删改只允许管理员
 */
@RestController
@RequestMapping("/api/banks")
@RequiredArgsConstructor
public class BankController {

    private final BankService bankService;
    private final AdminGuardService adminGuardService;

    @GetMapping
    public Result<PageResult<BankVO>> page(@RequestParam(required = false) String keyword,
                                           @RequestParam(required = false) String groupName,
                                           @RequestParam(required = false) String status,
                                           @RequestParam(defaultValue = "1") long page,
                                           @RequestParam(defaultValue = "10") long size) {
        return Result.ok(bankService.page(keyword, groupName, status, page, size));
    }

    @GetMapping("/all")
    public Result<List<BankVO>> all() {
        return Result.ok(bankService.listAll());
    }

    @GetMapping("/{id}")
    public Result<BankVO> detail(@PathVariable Long id) {
        return Result.ok(bankService.getById(id));
    }

    @PostMapping
    public Result<BankVO> create(@Valid @RequestBody BankForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(bankService.create(form));
    }

    @PutMapping("/{id}")
    public Result<BankVO> update(@PathVariable Long id, @Valid @RequestBody BankForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(bankService.update(id, form));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        adminGuardService.checkAdmin();
        bankService.delete(id);
        return Result.ok();
    }
}
