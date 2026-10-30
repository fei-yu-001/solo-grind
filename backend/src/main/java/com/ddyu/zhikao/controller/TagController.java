package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.TagForm;
import com.ddyu.zhikao.service.AdminGuardService;
import com.ddyu.zhikao.service.TagService;
import com.ddyu.zhikao.vo.TagVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 标签：列表 + 轻量增删
 */
@RestController
@RequestMapping("/api/tags")
@RequiredArgsConstructor
public class TagController {

    private final TagService tagService;
    private final AdminGuardService adminGuardService;

    @GetMapping
    public Result<List<TagVO>> list() {
        return Result.ok(tagService.list());
    }

    @PostMapping
    public Result<TagVO> create(@Valid @RequestBody TagForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(tagService.create(form));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        adminGuardService.checkAdmin();
        tagService.delete(id);
        return Result.ok();
    }
}
