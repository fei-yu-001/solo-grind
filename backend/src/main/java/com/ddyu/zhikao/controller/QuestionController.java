package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.QuestionBatchMoveDTO;
import com.ddyu.zhikao.dto.QuestionForm;
import com.ddyu.zhikao.service.AdminGuardService;
import com.ddyu.zhikao.service.QuestionService;
import com.ddyu.zhikao.vo.QuestionImportVO;
import com.ddyu.zhikao.vo.QuestionVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

/**
 * 题目管理：增删改只允许管理员
 */
@RestController
@RequestMapping("/api/questions")
@RequiredArgsConstructor
public class QuestionController {

    private final QuestionService questionService;
    private final AdminGuardService adminGuardService;

    @GetMapping
    public Result<PageResult<QuestionVO>> page(@RequestParam(required = false) Long bankId,
                                               @RequestParam(required = false) String type,
                                               @RequestParam(required = false) String keyword,
                                               @RequestParam(required = false) Integer difficulty,
                                               @RequestParam(required = false) Long tagId,
                                               @RequestParam(defaultValue = "1") long page,
                                               @RequestParam(defaultValue = "10") long size) {
        return Result.ok(questionService.page(bankId, type, keyword, difficulty, tagId, page, size));
    }

    @GetMapping("/{id}")
    public Result<QuestionVO> detail(@PathVariable Long id) {
        return Result.ok(questionService.getById(id));
    }

    @PostMapping
    public Result<QuestionVO> create(@Valid @RequestBody QuestionForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(questionService.create(form));
    }

    @PutMapping("/{id}")
    public Result<QuestionVO> update(@PathVariable Long id, @Valid @RequestBody QuestionForm form) {
        adminGuardService.checkAdmin();
        return Result.ok(questionService.update(id, form));
    }

    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        adminGuardService.checkAdmin();
        questionService.delete(id);
        return Result.ok();
    }

    /** 批量移动题目到题库 */
    @PatchMapping("/batch")
    public Result<Map<String, Integer>> batchMove(@Valid @RequestBody QuestionBatchMoveDTO dto) {
        adminGuardService.checkAdmin();
        int updated = questionService.batchMove(dto);
        return Result.ok(Map.of("updated", updated));
    }

    /** 从 Word 题库批量导入，只允许管理员 */
    @PostMapping("/import")
    public Result<QuestionImportVO> importDocx(@RequestParam("file") MultipartFile file,
                                               @RequestParam("bankId") Long bankId,
                                               @RequestParam(value = "difficulty", required = false) Integer difficulty) {
        adminGuardService.checkAdmin();
        return Result.ok(questionService.importDocx(file, bankId, difficulty));
    }
}
