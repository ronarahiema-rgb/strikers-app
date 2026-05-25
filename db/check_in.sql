CREATE TABLE check_in (
    check_in_id     INT             PRIMARY KEY AUTO_INCREMENT,
    student_id      INT             NOT NULL,
    mood            INT             NOT NULL,
    status          VARCHAR(255)    NOT NULL,
    focus_target    VARCHAR(255)    NOT NULL,
    backpack        INT             NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- foreign key
    CONSTRAINT fk_checkin_student
        FOREIGN KEY (student_id)
        REFERENCES student(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);