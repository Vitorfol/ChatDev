'''
Pydantic schemas for request and response validation used by the FastAPI endpoints.
This module defines:
- simple nested representations (CourseSimple, StudentSimple)
- base/create/update/read schemas for Student, Course, and Teacher
- validation for Course.level to normalize values and enforce allowed levels
- orm_mode enabled on read/simple schemas so SQLAlchemy models can be returned directly
The Course.level field is optional but, when provided, is normalized to a lowercase
string and validated to be one of: "beginner", "intermediate", or "advanced".
'''
from typing import List, Optional
from pydantic import BaseModel, EmailStr, validator
# Allowed course levels
_ALLOWED_LEVELS = {"beginner", "intermediate", "advanced"}
# Simple nested representations
class CourseSimple(BaseModel):
    id: int
    title: str
    level: Optional[str] = None
    class Config:
        orm_mode = True
class StudentSimple(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        orm_mode = True
# Student schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr
class StudentCreate(StudentBase):
    pass
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class StudentRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    courses: List[CourseSimple] = []
    class Config:
        orm_mode = True
# Course schemas
class CourseBase(BaseModel):
    title: str
    level: Optional[str] = None
    @validator("level")
    def validate_level(cls, v: Optional[str]) -> Optional[str]:
        """
        Normalize and validate the course level.
        Acceptable values (case-insensitive): beginner, intermediate, advanced.
        If None is provided, it is left as None.
        """
        if v is None:
            return None
        v_str = v.strip().lower()
        if v_str == "":
            return None
        if v_str not in _ALLOWED_LEVELS:
            raise ValueError(f"level must be one of: {', '.join(sorted(_ALLOWED_LEVELS))}")
        return v_str
class CourseCreate(CourseBase):
    teacher_id: Optional[int] = None
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
    teacher_id: Optional[int] = None
    @validator("level")
    def validate_level(cls, v: Optional[str]) -> Optional[str]:
        # Reuse the same normalization/validation logic as CourseBase
        if v is None:
            return None
        v_str = v.strip().lower()
        if v_str == "":
            return None
        if v_str not in _ALLOWED_LEVELS:
            raise ValueError(f"level must be one of: {', '.join(sorted(_ALLOWED_LEVELS))}")
        return v_str
class CourseRead(BaseModel):
    id: int
    title: str
    level: Optional[str] = None
    teacher_id: Optional[int] = None
    students: List[StudentSimple] = []
    class Config:
        orm_mode = True
# Teacher schemas
class TeacherBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
class TeacherCreate(TeacherBase):
    pass
class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class TeacherRead(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    courses: List[CourseSimple] = []
    class Config:
        orm_mode = True