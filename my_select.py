from db import engine
from models import Student, Grade, Subject, Group, Teacher
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

session = Session(engine)


def select_1():
    top_students = (
        session.query(Student, func.avg(Grade.grade_value).label("avg_grade"))
        .join(Grade, Grade.student_id == Student.id)
        .group_by(Student.id)
        .order_by(func.avg(Grade.grade_value).desc())
        .limit(5)
        .all()
    )
    return top_students


def select_2(subject_name):
    result = (
        session.query(Student, func.avg(Grade.grade_value).label("avg_grade"))
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .filter(Subject.name == subject_name)
        .group_by(Student.id)
        .order_by(func.avg(Grade.grade_value).desc())
        .first()
    )
    return result


def find_best_student_for_all_subjects():
    all_subjects = session.query(Subject).all()
    for subject in all_subjects:
        student_avg = select_2(subject.name)
        if student_avg:
            student, avg_grade = student_avg
            print(
                f"Найкращий студент з предмету '{subject.name}': {student.name} ({avg_grade:.2f})"
            )


def select_3(subject_name):
    results = (
        session.query(Group.name, func.avg(Grade.grade_value).label("avg_grade"))
        .join(Student, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .filter(Subject.name == subject_name)
        .group_by(Group.name)
        .all()
    )
    return results


def find_average_score_per_groups_for_all_subject():
    all_subjects = session.query(Subject).all()
    for subject in all_subjects:
        print(f"\nСередній бал у групах з предмету '{subject.name}':")
        results = select_3(subject.name)
        for group_name, avg_grade in results:
            print(f"{group_name}: {avg_grade:.2f}")


def select_4():
    avg = session.query(func.avg(Grade.grade_value)).scalar()
    print(f"Середній бал на потоці: {avg:.2f}")


def select_5(teacher_name):
    subjects = (
        session.query(Subject)
        .join(Teacher, Subject.teacher_id == Teacher.id)
        .filter(Teacher.name == teacher_name)
        .all()
    )

    print(f"Предмети, що викладає '{teacher_name}':")
    for subj in subjects:
        print(f"'{subj.name}'")


def find_subjects_for_all_teachers():
    teachers = session.query(Teacher).all()
    for teacher in teachers:
        select_5(teacher.name)


def select_6(group_name):
    students_in_group = (
        session.query(Student)
        .join(Group, Student.group_id == Group.id)
        .filter(Group.name == group_name)
        .all()
    )

    print(f"Список студентів групи '{group_name}'")
    for student in students_in_group:
        print(f"\n'{student.name}'")


def find_students_in_groups():
    groups = session.query(Group).all()
    for group in groups:
        select_6(group.name)


def select_7(subject_name, group_name):
    grades = (
        session.query(Student.name, Grade.grade_value)
        .join(Group, Student.group_id == Group.id)
        .join(Grade, Grade.student_id == Student.id)
        .join(Subject, Subject.id == Grade.subject_id)
        .filter(Group.name == group_name)
        .filter(Subject.name == subject_name)
        .order_by(Student.name)
        .all()
    )

    print(f"Оцінки студентів групи '{group_name}' з предмету '{subject_name}':")

    student_grades = defaultdict(list)
    for student_name, grade_value in grades:
        student_grades[student_name].append(grade_value)

    for student_name, grades_list in student_grades.items():
        print(f"\n{student_name}: {', '.join(map(str, grades_list))}")


def find_student_grades_in_all_subjects_per_groups():
    groups = session.query(Group).all()
    subjects = session.query(Subject).all()
    for group in groups:
        for subject in subjects:
            select_7(subject.name, group.name)


def select_8(teacher_name):
    avg_grade = (
        session.query(func.avg(Grade.grade_value))
        .join(Subject, Subject.id == Grade.subject_id)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .filter(Teacher.name == teacher_name)
        .scalar()
    )
    if avg_grade is not None:
        print(f"Середній бал, який ставить викладач {teacher_name}: {avg_grade:.2f}")
    else:
        print(f"Викладач {teacher_name} ще не має оцінок.")


def find_average_grade_for_teachers():
    teachers = session.query(Teacher).all()
    for teacher in teachers:
        select_8(teacher.name)


def select_9(student_name):
    subjects = (
        session.query(Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Student.id == Grade.student_id)
        .filter(Student.name == student_name)
        .distinct()
        .all()
    )

    print(f"Курси, які відвідує студент {student_name}:")
    for (subject_name,) in subjects:
        print(f"- {subject_name}")


def find_subjects_for_students():
    students = session.query(Student).all()
    for student in students:
        select_9(student.name)


def select_10(student_name, teacher_name):
    subjects = (
        session.query(Subject.name)
        .join(Grade, Grade.subject_id == Subject.id)
        .join(Student, Student.id == Grade.student_id)
        .join(Teacher, Teacher.id == Subject.teacher_id)
        .filter(Student.name == student_name)
        .filter(Teacher.name == teacher_name)
        .distinct()
        .all()
    )

    print(f"Курси, які відвідує студент {student_name} у викладача {teacher_name}:")
    for (subject_name,) in subjects:
        print(f"- {subject_name}")


def find_subjects_for_students_with_teacher():
    students = session.query(Student).all()
    teachers = session.query(Teacher).all()
    for student in students:
        for teacher in teachers:
            select_10(student.name, teacher.name)


top_students = select_1()
print("Топ 5 студентів за середнім балом:")
for student, avg in top_students:
    print(f"{student.name}: {avg:.2f}")

find_best_student_for_all_subjects()
find_average_score_per_groups_for_all_subject()
select_4()
find_subjects_for_all_teachers()
find_students_in_groups()
find_student_grades_in_all_subjects_per_groups()
find_average_grade_for_teachers()
find_subjects_for_students()
find_subjects_for_students_with_teacher()
