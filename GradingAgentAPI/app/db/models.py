from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    criteria = relationship("Criteria", back_populates="assignment", uselist=False)
    grading_results = relationship("GradingResult", back_populates="assignment")

class Criteria(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    natural_language_rubric = Column(Text)  # Natural language grading instructions for Gemini
    regex_checks = Column(JSON, nullable=True)  # Optional list of regex checks for automatic deductions

    assignment = relationship("Assignment", back_populates="criteria")

class GradingResult(Base):
    __tablename__ = "grading_results"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(String, index=True)
    grade = Column(Float)
    feedback = Column(Text)

    assignment = relationship("Assignment", back_populates="grading_results")
