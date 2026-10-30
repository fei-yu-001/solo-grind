package com.ddyu.zhikao.service;

import com.ddyu.zhikao.dto.AnswerSubmitDTO;
import com.ddyu.zhikao.vo.ScoreVO;

public interface AnswerService {

    /** 交卷判分，事务。同一考生同一试卷只能交一次 */
    ScoreVO submit(AnswerSubmitDTO dto, Long userId);
}
