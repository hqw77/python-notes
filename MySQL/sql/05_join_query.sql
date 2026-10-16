USE py_adv_db;

-- 1. INNER JOIN：只显示有选课记录的学生
SELECT s.name AS 学生, c.name AS 课程, e.score AS 成绩
FROM
    enrollments e
    INNER JOIN students s ON e.student_id = s.id
    INNER JOIN courses c ON e.course_id = c.id
ORDER BY s.name, c.name;

-- 2. LEFT JOIN：所有学生，包括没选课的
SELECT s.name AS 学生, c.name AS 课程, e.score AS 成绩
FROM
    students s
    LEFT JOIN enrollments e ON s.id = e.student_id
    LEFT JOIN courses c ON e.course_id = c.id
ORDER BY s.name;

-- 3. LEFT JOIN：所有课程，包括没人选的
SELECT c.name AS 课程, COUNT(e.student_id) AS 选课人数
FROM courses c
    LEFT JOIN enrollments e ON c.id = e.course_id
GROUP BY
    c.id,
    c.name;

-- 4. 三表连接 + 条件
SELECT s.name, c.name, e.score
FROM
    enrollments e
    JOIN students s ON e.student_id = s.id
    JOIN courses c ON e.course_id = c.id
WHERE
    e.score >= 85
ORDER BY e.score DESC;