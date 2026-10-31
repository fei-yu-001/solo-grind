package com.ddyu.zhikao.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/** 导入时单行解析失败 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class QuestionImportErrorVO {

    private String line;
    private String reason;
}
