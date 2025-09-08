from db import engine
from models import Student, Grade, Subject, Group, Teacher
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

session = Session(engine)


def find_5_most_success_students():
    top_students = (
        session.query(Student, func.avg(Grade.grade_value).label("avg_grade"))
        .join(Grade, Grade.student_id == Student.id)
        .group_by(Student.id)
        .order_by(func.avg(Grade.grade_value).desc())
        .limit(5)
        .all()
    )
    return top_students


def find_best_student_from_subject(subject_name):
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
        student_avg = find_best_student_from_subject(subject.name)
        if student_avg:
            student, avg_grade = student_avg
            print(
                f"Найкращий студент з предмету '{subject.name}': {student.name} ({avg_grade:.2f})"
            )


def find_average_score_per_groups_for_subject(subject_name):
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
        results = find_average_score_per_groups_for_subject(subject.name)
        for group_name, avg_grade in results:
            print(f"{group_name}: {avg_grade:.2f}")


def find_average_score_all():
    avg = session.query(func.avg(Grade.grade_value)).scalar()
    print(f"Середній бал на потоці: {avg:.2f}")


def find_subject_by_teacher(teacher_name):
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
        find_subject_by_teacher(teacher.name)


def find_students_in_group(group_name):
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
        find_students_in_group(group.name)


def find_subject_grades_in_group(subject_name, group_name):
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
            find_subject_grades_in_group(subject.name, group.name)


def find_average_grade_for_teacher(teacher_name):
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
        find_average_grade_for_teacher(teacher.name)


def find_subjects_for_student(student_name):
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
        find_subjects_for_student(student.name)


def find_subject_for_student_with_teacher(student_name, teacher_name):
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
            find_subject_for_student_with_teacher(student.name, teacher.name)


top_students = find_5_most_success_students()
print("Топ 5 студентів за середнім балом:")
for student, avg in top_students:
    print(f"{student.name}: {avg:.2f}")

find_best_student_for_all_subjects()
find_average_score_per_groups_for_all_subject()
find_average_score_all()
find_subjects_for_all_teachers()
find_students_in_groups()
find_student_grades_in_all_subjects_per_groups()
find_average_grade_for_teachers()
find_subjects_for_students()
find_subjects_for_students_with_teacher()
