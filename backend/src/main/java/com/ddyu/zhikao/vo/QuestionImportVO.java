package com.ddyu.zhikao.vo;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/** Word 题库导入结果 */
@Data
public class QuestionImportVO {

    private int imported;
    private int skipped;
    private List<QuestionImportErrorVO> errors = new ArrayList<>();
}
