package com.ddyu.zhikao.service;

import com.ddyu.zhikao.common.PageResult;
import com.ddyu.zhikao.dto.QuestionBatchMoveDTO;
import com.ddyu.zhikao.dto.QuestionForm;
import com.ddyu.zhikao.vo.QuestionImportVO;
import com.ddyu.zhikao.vo.QuestionVO;
import org.springframework.web.multipart.MultipartFile;

public interface QuestionService {

    PageResult<QuestionVO> page(Long bankId, String type, String keyword, Integer difficulty, Long tagId,
                                long page, long size);

    QuestionVO getById(Long id);

    QuestionVO create(QuestionForm form);

    QuestionVO update(Long id, QuestionForm form);

    /** 被试卷引用时 409 */
    void delete(Long id);

    /** 批量移动题目到题库，事务 */
    int batchMove(QuestionBatchMoveDTO dto);

    /** 从 docx 批量导入题目，整批一个事务 */
    QuestionImportVO importDocx(MultipartFile file, Long bankId, Integer difficulty);
}
