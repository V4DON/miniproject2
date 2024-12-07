from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Boolean, ForeignKey, Enum, Text
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import ENUM

Base = declarative_base()

# ENUM типы
education_level = ('Среднее профессиональное', 'Высшее')
marital_status = ('Холост/Не замужем', 'Женат/За мужем', 'Разведён/Разведена', 'Вдова/Вдовец')
department_type = ('Отдел продаж', 'Бухгалтерия', 'IT отдел')
training_type = ('Повышение квалификации', 'Переподготовка', 'Новое образование')
training_format = ('Очное', 'Дистанционное', 'Гибридное')


class TrainingPlace(Base):
    __tablename__ = 'TrainingPlace'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)


class Qualification(Base):
    __tablename__ = 'Qualification'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)


class Specialty(Base):
    __tablename__ = 'Specialty'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    short_name = Column(String, nullable=False)
    qualification_id = Column(Integer, ForeignKey('Qualification.id'))
    qualification = relationship('Qualification')


class Document(Base):
    __tablename__ = 'Document'
    id = Column(Integer, primary_key=True)
    series = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    issue_date = Column(Date, nullable=False)
    issued_by = Column(Text, nullable=False)


class Education(Base):
    __tablename__ = 'Education'
    id = Column(Integer, primary_key=True)
    level = Column(ENUM(*education_level, name='education_level', create_type=False), nullable=False)
    series = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    registration_number = Column(Integer, nullable=False)
    issue_date = Column(Date, nullable=False)
    specialty_id = Column(Integer, ForeignKey('Specialty.id'))
    specialty = relationship('Specialty')


class Employee(Base):
    __tablename__ = 'Employee'
    id = Column(Integer, primary_key=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String)
    phone_number = Column(String)
    birth_date = Column(Date, nullable=False)
    snils = Column(String, nullable=False)
    inn = Column(String, nullable=False)
    passport_id = Column(Integer, ForeignKey('Document.id'))
    work_experience_years = Column(Integer, nullable=False)
    marital_status = Column(ENUM(*marital_status, name='marital_status', create_type=False), nullable=False)
    employment_date = Column(Date, nullable=False)
    termination_date = Column(Date)
    delete = Column(Boolean)
    passport = relationship('Document')


class EmployeeEducation(Base):
    __tablename__ = 'EmployeeEducation'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    education_id = Column(Integer, ForeignKey('Education.id'))
    employee = relationship('Employee')
    education = relationship('Education')


class Position(Base):
    __tablename__ = 'Position'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)


class EmployeePosition(Base):
    __tablename__ = 'EmployeePosition'
    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey('Position.id'))
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    department = Column(ENUM(*department_type, name='department_type', create_type=False), nullable=False)
    position = relationship('Position')
    employee = relationship('Employee')


class Training(Base):
    __tablename__ = 'Training'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(ENUM(*training_type, name='training_type', create_type=False), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    format = Column(ENUM(*training_format, name='training_format', create_type=False), nullable=False)
    training_place_id = Column(Integer, ForeignKey('TrainingPlace.id'))
    training_place = relationship('TrainingPlace')


class EmployeeTraining(Base):
    __tablename__ = 'EmployeeTraining'
    id = Column(Integer, primary_key=True)
    training_id = Column(Integer, ForeignKey('Training.id'))
    employee_id = Column(Integer, ForeignKey('Employee.id'))
    training_completed = Column(Boolean, nullable=False)
    document_number = Column(String)
    training = relationship('Training')
    employee = relationship('Employee')


# Соединение
class Connect():
    def create_connection():
        engine = create_engine("postgresql://postgres@localhost:5432/postgres")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
