USE py_adv_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS enrollments;

DROP TABLE IF EXISTS courses;

SET FOREIGN_KEY_CHECKS = 1;

-- 课程表
CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    teacher VARCHAR(50)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 选课表
CREATE TABLE enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    score DECIMAL(5, 2),
    FOREIGN KEY (student_id) REFERENCES students (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- 初始数据
INSERT INTO
    courses (name, teacher)
VALUES ('Python 基础', '王老师'),
    ('数据库原理', '李老师'),
    ('Web 开发', '张老师');

INSERT INTO
    enrollments (student_id, course_id, score)
VALUES (1, 1, 88.5),
    (1, 2, 92.0),
    (2, 1, 76.5),
    (2, 3, 85.0),
    (3, 2, 90.0);

SELECT * FROM courses;

SELECT * FROM enrollments;