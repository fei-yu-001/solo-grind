package com.ddyu.zhikao.service;

import com.ddyu.zhikao.vo.ExamCardVO;
import com.ddyu.zhikao.vo.ExamPaperViewVO;

import java.util.List;

public interface ExamRoomService {

    /** 考试中心：PUBLISHED 试卷 + 当前考生作答状态 */
    List<ExamCardVO> available(Long userId);

    /** 进考场：无答案的题目列表，非 PUBLISHED 或已交卷 409 */
    ExamPaperViewVO getExamView(Long paperId, Long userId);
}
