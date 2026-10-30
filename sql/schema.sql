-- 智考 · 刷题考试系统 · 建表脚本
-- MySQL 8.0，字符集 utf8mb4
-- 关系覆盖：一对一（sys_user ↔ user_profile）
--           一对多（question_bank → question，exam_paper → answer_record，sys_user → answer_record）
--           多对多（question ↔ tag，exam_paper ↔ question）

DROP DATABASE IF EXISTS zhikao;
CREATE DATABASE zhikao DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zhikao;

-- 登录账号：管理员和考生共用一张表，用 role 区分
CREATE TABLE sys_user (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    username    VARCHAR(32)  NOT NULL COMMENT '登录名',
    password    VARCHAR(100) NOT NULL COMMENT 'BCrypt 哈希',
    nickname    VARCHAR(32)  NOT NULL COMMENT '昵称',
    role        VARCHAR(16)  NOT NULL DEFAULT 'STUDENT' COMMENT 'ADMIN 管理员 / STUDENT 考生',
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1 启用 0 停用',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_username (username)
) ENGINE = InnoDB COMMENT '登录账号';

-- 一对一：一个账号一份资料，user_id 加唯一约束
CREATE TABLE user_profile (
    id          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id     BIGINT      NOT NULL COMMENT '账号主键（唯一，构成一对一）',
    school      VARCHAR(64)          DEFAULT NULL COMMENT '学校',
    group_name  VARCHAR(16)          DEFAULT NULL COMMENT '本科组 / 专科组',
    phone       VARCHAR(20)          DEFAULT NULL COMMENT '手机号',
    avatar      VARCHAR(200)         DEFAULT NULL COMMENT '头像地址',
    PRIMARY KEY (id),
    UNIQUE KEY uk_profile_user (user_id),
    CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES sys_user (id)
) ENGINE = InnoDB COMMENT '考生资料';

CREATE TABLE question_bank (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    name        VARCHAR(64)  NOT NULL COMMENT '题库名',
    group_name  VARCHAR(16)  NOT NULL COMMENT '本科组 / 专科组',
    description VARCHAR(255)          DEFAULT NULL COMMENT '题库说明',
    status      VARCHAR(16)  NOT NULL DEFAULT 'ENABLED' COMMENT 'ENABLED 启用 / DISABLED 停用',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_bank_name (name)
) ENGINE = InnoDB COMMENT '题库';

CREATE TABLE tag (
    id     BIGINT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    name   VARCHAR(32) NOT NULL COMMENT '知识点名称',
    color  VARCHAR(16)          DEFAULT NULL COMMENT '展示颜色',
    PRIMARY KEY (id),
    UNIQUE KEY uk_tag_name (name)
) ENGINE = InnoDB COMMENT '知识点标签';

-- 一对多：一个题库下有多道题
CREATE TABLE question (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    bank_id     BIGINT       NOT NULL COMMENT '所属题库',
    type        VARCHAR(16)  NOT NULL COMMENT 'single 单选 / multi 多选 / judge 判断',
    stem        TEXT         NOT NULL COMMENT '题干',
    options     JSON                  DEFAULT NULL COMMENT '选项数组 [{"key":"A","text":"..."}]',
    answer      JSON         NOT NULL COMMENT '答案，单选 "B"、多选 ["A","C"]、判断 "A"/"B"',
    analysis    TEXT                  DEFAULT NULL COMMENT '解析',
    difficulty  TINYINT      NOT NULL DEFAULT 1 COMMENT '1 易 / 2 中 / 3 难',
    sort_no     INT          NOT NULL DEFAULT 0 COMMENT '题库内序号',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_question_bank (bank_id),
    KEY idx_question_type (type),
    CONSTRAINT fk_question_bank FOREIGN KEY (bank_id) REFERENCES question_bank (id)
) ENGINE = InnoDB COMMENT '题目';

-- 多对多中间表：一道题多个知识点，一个知识点多道题
CREATE TABLE question_tag (
    question_id BIGINT NOT NULL COMMENT '题目主键',
    tag_id      BIGINT NOT NULL COMMENT '标签主键',
    PRIMARY KEY (question_id, tag_id),
    KEY idx_qt_tag (tag_id),
    CONSTRAINT fk_qt_question FOREIGN KEY (question_id) REFERENCES question (id) ON DELETE CASCADE,
    CONSTRAINT fk_qt_tag FOREIGN KEY (tag_id) REFERENCES tag (id)
) ENGINE = InnoDB COMMENT '题目标签关联';

CREATE TABLE exam_paper (
    id           BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
    title        VARCHAR(64)  NOT NULL COMMENT '试卷名',
    bank_id      BIGINT       NOT NULL COMMENT '来源题库',
    judge_count  INT          NOT NULL DEFAULT 0 COMMENT '判断题数量',
    single_count INT          NOT NULL DEFAULT 0 COMMENT '单选题数量',
    multi_count  INT          NOT NULL DEFAULT 0 COMMENT '多选题数量',
    judge_score  INT          NOT NULL DEFAULT 1 COMMENT '判断题每题分值',
    single_score INT          NOT NULL DEFAULT 1 COMMENT '单选题每题分值',
    multi_score  INT          NOT NULL DEFAULT 2 COMMENT '多选题每题分值',
    duration_sec INT          NOT NULL DEFAULT 3600 COMMENT '考试时长（秒）',
    total_score  INT          NOT NULL DEFAULT 0 COMMENT '总分',
    status       VARCHAR(16)  NOT NULL DEFAULT 'DRAFT' COMMENT 'DRAFT 草稿 / PUBLISHED 已发布 / CLOSED 已结束',
    created_by   BIGINT                DEFAULT NULL COMMENT '创建人',
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_paper_bank (bank_id),
    KEY idx_paper_status (status),
    CONSTRAINT fk_paper_bank FOREIGN KEY (bank_id) REFERENCES question_bank (id)
) ENGINE = InnoDB COMMENT '试卷';

-- 多对多中间表：一张试卷多道题，一道题可进多张试卷，带题序与分值
CREATE TABLE exam_paper_question (
    paper_id    BIGINT NOT NULL COMMENT '试卷主键',
    question_id BIGINT NOT NULL COMMENT '题目主键',
    seq         INT    NOT NULL COMMENT '题序，从 1 开始',
    score       INT    NOT NULL COMMENT '本题分值',
    PRIMARY KEY (paper_id, question_id),
    KEY idx_pq_question (question_id),
    CONSTRAINT fk_pq_paper FOREIGN KEY (paper_id) REFERENCES exam_paper (id) ON DELETE CASCADE,
    CONSTRAINT fk_pq_question FOREIGN KEY (question_id) REFERENCES question (id)
) ENGINE = InnoDB COMMENT '试卷题目关联';

-- 作答记录：一次考试中某考生对某题的作答，交卷时批量写入
CREATE TABLE answer_record (
    id           BIGINT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    paper_id     BIGINT      NOT NULL COMMENT '试卷',
    user_id      BIGINT      NOT NULL COMMENT '考生',
    question_id  BIGINT      NOT NULL COMMENT '题目',
    chosen       JSON                 DEFAULT NULL COMMENT '考生作答，未答为 null',
    correct      TINYINT     NOT NULL DEFAULT 0 COMMENT '1 正确 0 错误',
    score        INT         NOT NULL DEFAULT 0 COMMENT '本题得分',
    submitted_at DATETIME             DEFAULT NULL COMMENT '交卷时间',
    PRIMARY KEY (id),
    KEY idx_answer_paper_user (paper_id, user_id),
    KEY idx_answer_user (user_id),
    KEY idx_answer_question (question_id),
    CONSTRAINT fk_answer_paper FOREIGN KEY (paper_id) REFERENCES exam_paper (id),
    CONSTRAINT fk_answer_user FOREIGN KEY (user_id) REFERENCES sys_user (id),
    CONSTRAINT fk_answer_question FOREIGN KEY (question_id) REFERENCES question (id)
) ENGINE = InnoDB COMMENT '作答记录';
