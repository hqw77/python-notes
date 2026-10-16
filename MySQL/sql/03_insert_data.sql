USE py_adv_db;

-- 先清空再插入，保证脚本可重复执行
-- 注意: 不能用 TRUNCATE。因为 04 建的 enrollments 表外键引用了 students,
-- TRUNCATE 被外键引用的表会报错 1701。改用 DELETE + 关闭外键检查 + 重置自增。
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM students;
ALTER TABLE students AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO
    students (name, age, email)
VALUES (
        '张三',
        20,
        'zhangsan@example.com'
    ),
    ('李四', 22, 'lisi@example.com'),
    (
        '王五',
        21,
        'wangwu@example.com'
    );

SELECT * FROM students;