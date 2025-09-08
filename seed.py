import random
from faker import Faker
from sqlalchemy.orm import Session
from db import engine
from models import Base, Student, Teacher, Group, Subject, Grade

fake = Faker("uk_UA")


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        teachers = [Teacher(name=fake.name()) for _ in range(4)]
        session.add_all(teachers)

        groups = [Group(name=f"Group {i}") for i in range(1, 4)]
        session.add_all(groups)

        subjects = [
            Subject(name=fake.word().capitalize(), teacher=random.choice(teachers))
            for _ in range(6)
        ]
        session.add_all(subjects)
        session.flush()

        students = [
            Student(name=fake.name(), group=random.choice(groups)) for _ in range(40)
        ]
        session.add_all(students)

        session.flush()

        grades = []
        for student in students:
            for subject in random.sample(subjects, k=len(subjects)):
                for _ in range(random.randint(5, 20)):
                    grade = Grade(
                        student=student,
                        subject=subject,
                        grade_value=random.randint(1, 12),
                        date_received=fake.date_time_this_year(),
                    )
                    grades.append(grade)
        session.add_all(grades)

        session.commit()


if __name__ == "__main__":
    seed()
