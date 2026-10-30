package com.ddyu.zhikao.controller;

import com.ddyu.zhikao.common.LoginContext;
import com.ddyu.zhikao.common.Result;
import com.ddyu.zhikao.dto.AnswerSubmitDTO;
import com.ddyu.zhikao.service.AnswerService;
import com.ddyu.zhikao.vo.ScoreVO;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 考生交卷，判分在 Service
 */
@RestController
@RequestMapping("/api/answers")
@RequiredArgsConstructor
public class AnswerController {

    private final AnswerService answerService;

    @PostMapping("/submit")
    public Result<ScoreVO> submit(@Valid @RequestBody AnswerSubmitDTO dto) {
        Long userId = LoginContext.get().getId();
        return Result.ok(answerService.submit(dto, userId));
    }
}
