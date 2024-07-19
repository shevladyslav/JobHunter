from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

user_vacancy_association = Table(
    "user_vacancy_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("vacancy_id", Integer, ForeignKey("vacancies.id")),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    task_status = Column(Boolean, default=False)

    vacancies = relationship(
        "Vacancy", secondary=user_vacancy_association, back_populates="users"
    )


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    publication_date = Column(DateTime, nullable=False)
    vacancy_link = Column(String, nullable=False)

    users = relationship(
        "User", secondary=user_vacancy_association, back_populates="vacancies"
    )
