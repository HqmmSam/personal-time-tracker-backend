-- Personal Time Tracker · 数据库初始化脚本
-- 包含：users / projects / tasks / time_records / user_settings 五张表
-- 字符集：utf8mb4，引擎：InnoDB

CREATE DATABASE IF NOT EXISTS time_tracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    COMMENT '个人时间追踪器';

USE time_tracker;


-- ============================================================
-- users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    email           VARCHAR(100)    NOT NULL COMMENT '登录邮箱，全局唯一',
    password_hash   VARCHAR(60)     NOT NULL COMMENT 'bcrypt 哈希',
    nickname        VARCHAR(50)     NOT NULL DEFAULT '',
    avatar          VARCHAR(500)    DEFAULT NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP       NULL DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- ============================================================
-- projects
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL,
    name            VARCHAR(100)    NOT NULL,
    color           VARCHAR(7)      NOT NULL DEFAULT '#3b82f6',
    description     TEXT            DEFAULT NULL,
    due_date        DATE            DEFAULT NULL,
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP       NULL DEFAULT NULL,
    PRIMARY KEY (id),
    KEY idx_user_deleted (user_id, deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';


-- ============================================================
-- tasks
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '冗余字段，避免权限校验时 JOIN projects',
    project_id      BIGINT UNSIGNED NOT NULL,
    name            VARCHAR(100)    NOT NULL,
    note            TEXT            DEFAULT NULL,
    status          ENUM('active','completed','archived') NOT NULL DEFAULT 'active',
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP       NULL DEFAULT NULL,
    PRIMARY KEY (id),
    KEY idx_user_deleted (user_id, deleted_at),
    KEY idx_project_deleted (project_id, deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';


-- ============================================================
-- time_records
-- ============================================================
CREATE TABLE IF NOT EXISTS time_records (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL,
    task_id         BIGINT UNSIGNED NOT NULL,
    record_date     DATE            NOT NULL,
    start_time      DATETIME        DEFAULT NULL,
    duration        INT UNSIGNED    NOT NULL COMMENT '秒数',
    type            ENUM('auto','manual') NOT NULL DEFAULT 'auto',
    note            TEXT            DEFAULT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_user_date (user_id, record_date),
    KEY idx_task (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='时间记录表';


-- ============================================================
-- user_settings
-- ============================================================
CREATE TABLE IF NOT EXISTS user_settings (
    user_id             BIGINT UNSIGNED NOT NULL,
    daily_goal_minutes  INT             NOT NULL DEFAULT 240,
    dark_mode           TINYINT(1)      NOT NULL DEFAULT 0,
    timezone            VARCHAR(50)     NOT NULL DEFAULT 'Asia/Shanghai',
    week_start          TINYINT         NOT NULL DEFAULT 1,
    created_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户设置表';
