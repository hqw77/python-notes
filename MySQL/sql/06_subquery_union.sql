USE py_adv_db;

-- 1. 子查询：选了「Python 基础」的学生
SELECT name
FROM students
WHERE
    id IN (
        SELECT student_id
        FROM enrollments
        WHERE
            course_id = (
                SELECT id
                FROM courses
                WHERE
                    name = 'Python 基础'
            )
    );

-- 2. 子查询：成绩高于平均分的学生
SELECT s.name, e.score
FROM enrollments e
    JOIN students s ON e.student_id = s.id
WHERE
    e.score > (
        SELECT AVG(score)
        FROM enrollments
    )
ORDER BY e.score DESC;

-- 3. 子查询：没选任何课的学生
SELECT name
FROM students
WHERE
    id NOT IN(
        SELECT DISTINCT
            student_id
        FROM enrollments
    );

-- 4. UNION：合并两表姓名（去重）
SELECT name FROM students UNION SELECT teacher FROM courses;

-- 5. UNION ALL：不去重
SELECT name FROM students UNION ALL SELECT teacher FROM courses;