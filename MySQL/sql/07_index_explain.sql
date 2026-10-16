USE py_adv_db;

-- 1. 看没索引时的执行计划
EXPLAIN SELECT * FROM students WHERE email = 'lisi@example.com';
-- 注意 type 列、key 列、rows 列

-- 2. 建索引
CREATE INDEX idx_students_age ON students (age);

-- 3. 再看一次执行计划（对比）
EXPLAIN SELECT * FROM students WHERE age = 20;

-- 4. 组合索引
CREATE INDEX idx_enroll_stu_course ON enrollments (student_id, course_id);

EXPLAIN
SELECT *
FROM enrollments
WHERE
    student_id = 1
    AND course_id = 2;

-- 5. 查看某表所有索引
SHOW INDEX FROM students;

-- 6. 删除索引
-- DROP INDEX idx_students_age ON students;