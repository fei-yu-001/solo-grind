package com.ddyu.zhikao.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 作答记录，交卷时批量写入
 */
@Data
@TableName("answer_record")
public class AnswerRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long paperId;

    private Long userId;

    private Long questionId;

    /** 考生作答 JSON 字符串，未答为 null */
    private String chosen;

    /** 1 正确 0 错误 */
    private Integer correct;

    private Integer score;

    private LocalDateTime submittedAt;
}
