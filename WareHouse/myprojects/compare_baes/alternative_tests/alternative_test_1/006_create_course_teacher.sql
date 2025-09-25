'''
Create course_teacher association table for teacher-course relationship.
'''
-- Create course_teacher association table for teacher-course relationship.
CREATE TABLE IF NOT EXISTS course_teacher (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    UNIQUE(course_id, teacher_id),
    FOREIGN KEY(course_id) REFERENCES course(id) ON DELETE CASCADE,
    FOREIGN KEY(teacher_id) REFERENCES teacher(id) ON DELETE CASCADE
);