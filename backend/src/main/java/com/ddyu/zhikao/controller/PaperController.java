package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.PaperForm;
import com.ddyu.zhikao.service.AdminGuardService;
import com.ddyu.zhikao.service.PaperService;
import com.ddyu.zhikao.vo.PaperDetailVO;
import com.ddyu.zhikao.vo.PaperVO;
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

/**
 * 试卷管理：组卷、状态流转只允许管理员
 */
@RestController
@RequestMapping("/api/papers")
@RequiredArgsConstructor
public class PaperController {

    private final PaperService paperService;
    private final AdminGuardService adminGuardService;

    @GetMapping
    public Result<PageResult<PaperVO>> page(@RequestParam(required = false) String keyword,
                                            @RequestParam(required = false) String status,
                                            @RequestParam(required = false) Long bankId,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "10") long size) {
        return Result.ok(paperService.page(keyword, status, bankId, page, size));
    }

    @GetMapping("/{id}")
    public Result<PaperDetailVO> detail(@PathVariable Long id) {
        return Result.ok(paperService.getDetail(id));
    }

    @PostMapping
    public Result<PaperVO> create(@Valid @RequestBody PaperForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(paperService.create(form, adminGuardService.currentUser().getId()));
    }

    @PutMapping("/{id}")
    public Result<PaperVO> update(@PathVariable Long id, @Valid @RequestBody PaperForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(paperService.update(id, form));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        adminGuardService.checkAdmin();
        paperService.delete(id);
        return Result.ok();
    }

    @PostMapping("/{id}/publish")
    public Result<PaperVO> publish(@PathVariable Long id) {
        adminGuardService.checkAdmin();
        return Result.ok(paperService.publish(id));
    }

    @PostMapping("/{id}/close")
    public Result<PaperVO> close(@PathVariable Long id) {
        adminGuardService.checkAdmin();
        return Result.ok(paperService.close(id));
    }
}
