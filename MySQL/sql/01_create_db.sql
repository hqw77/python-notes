-- 建库（幂等，可重复执行）
CREATE DATABASE IF NOT EXISTS py_adv_db DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;

-- 切换并确认
USE py_adv_db;

SELECT DATABASE();