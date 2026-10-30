package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.LoginContext;
import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.service.ExamRoomService;
import com.ddyu.zhikao.vo.ExamCardVO;
import com.ddyu.zhikao.vo.ExamPaperViewVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * 考生在线答题：考试中心 + 进考场，对 STUDENT 开放
 */
@RestController
@RequestMapping("/api/exams")
@RequiredArgsConstructor
public class ExamController {

    private final ExamRoomService examRoomService;

    @GetMapping("/available")
    public Result<List<ExamCardVO>> available() {
        return Result.ok(examRoomService.available(LoginContext.get().getId()));
    }

    @GetMapping("/{paperId}/questions")
    public Result<ExamPaperViewVO> questions(@PathVariable Long paperId) {
        return Result.ok(examRoomService.getExamView(paperId, LoginContext.get().getId()));
    }
}
