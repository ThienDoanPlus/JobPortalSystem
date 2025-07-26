from enum import Enum
from sqlalchemy import Enum as SqlEnum
from . import db
from datetime import datetime
from enum import Enum as PyEnum
from flask_login import UserMixin


class RoleEnum(PyEnum):
    ADMIN = 'admin'
    RECRUITER = 'recruiter'
    CANDIDATE = 'candidate'


class JobTypeEnum(PyEnum):
    FULL_TIME = 'Toàn thời gian'
    PART_TIME = 'Bán thời gian'
    CONTRACT = 'Hợp đồng'
    FREELANCE = 'Freelancer'
    INTERNSHIP = 'Thực tập'

class PaymentStatusEnum(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class ExperienceLevelEnum(PyEnum):
    INTERN = 'Thực tập sinh'
    FRESHER = 'Fresher'
    JUNIOR = 'Junior'
    SENIOR = 'Senior'
    MANAGER = 'Quản lý'


class ApplicationStatusEnum(PyEnum):
    RECEIVED = 'Đã nhận'
    VIEWED = 'Đã xem'
    INTERVIEWING = 'Mời phỏng vấn'
    REJECTED = 'Từ chối'
    OFFERED = 'Mời nhận việc'


class VerificationStatusEnum(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    avatar = db.Column(db.String(255))

    # Relationships trỏ đến các hồ sơ chuyên biệt
    recruiter_profile = db.relationship("Company", back_populates="user", uselist=False)
    candidate_profile = db.relationship("CandidateProfile", back_populates="user", uselist=False)


class CandidateProfile(BaseModel):
    __tablename__ = 'candidate_profile'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    linkedin_url = db.Column(db.String(255))

    user = db.relationship("User", back_populates="candidate_profile")
    resumes = db.relationship("Resume", backref="candidate", lazy="dynamic")  # Một ứng viên có nhiều CV

    applications = db.relationship("Application", backref="candidate")


# --- RESUME MODELS (Requirement 1): Xây dựng hệ thống CV online chi tiết ---

class Resume(BaseModel):
    __tablename__ = 'resume'
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profile.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False, comment="VD: CV ứng tuyển Python Developer")
    cv_file_path = db.Column(db.String(255), nullable=True)

    # Một CV có nhiều kinh nghiệm, học vấn, kỹ năng...
    experiences = db.relationship("Experience", backref="resume", lazy=True, cascade="all, delete-orphan")
    educations = db.relationship("Education", backref="resume", lazy=True, cascade="all, delete-orphan")
    skills = db.relationship("Skill", backref="resume", lazy=True, cascade="all, delete-orphan")


class Experience(BaseModel):
    __tablename__ = 'experience'
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_title = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)


class Education(BaseModel):
    __tablename__ = 'education'
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    institution_name = db.Column(db.String(255))
    degree = db.Column(db.String(255))
    major = db.Column(db.String(255))
    graduation_date = db.Column(db.Date)


class Skill(BaseModel):
    __tablename__ = 'skill'
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    skill_name = db.Column(db.String(100))


# --- EMPLOYER & JOB MODELS:---

class Company(BaseModel):  # hồ sơ của nhà tuyển dụng
    __tablename__ = 'company'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    tax_code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    website = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="recruiter_profile")
    images = db.relationship("CompanyImage", backref="company", lazy=True, cascade="all, delete-orphan")
    job_posts = db.relationship("JobPost", backref="company", lazy="dynamic")
    reviews = db.relationship("CompanyReview", backref="company", lazy="dynamic")
    followers = db.relationship("Follow", backref="company", lazy="dynamic")


class CompanyImage(BaseModel):
    __tablename__ = 'company_image'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)  # URL Cloudinary


class Category(BaseModel):  # Bảng danh mục ngành nghề để chuẩn hóa dữ liệu
    __tablename__ = 'category'
    name = db.Column(db.String(100), unique=True, nullable=False)
    job_posts = db.relationship("JobPost", backref="category", lazy=True)


class JobPost(BaseModel):
    __tablename__ = 'job_post'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)  # Liên kết với danh mục
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)

    # Cải thiện các trường để lọc
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    job_type = db.Column(db.Enum(JobTypeEnum), nullable=False)
    experience_level = db.Column(db.Enum(ExperienceLevelEnum), nullable=False)

    location = db.Column(db.String(255))
    deadline = db.Column(db.Date)

    applications = db.relationship("Application", backref="job", lazy="dynamic")


# --- APPLICATION & INTERACTION MODELS ---

class Application(BaseModel):
    __tablename__ = 'application'
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profile.id'), nullable=False)

    # Cho phép ứng tuyển bằng CV online hoặc tải file lên
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=True)  # CV online đã tạo
    cv_file_url = db.Column(db.String(255), nullable=True)  # File PDF/Word tải lên

    status = db.Column(db.Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.RECEIVED)
    employer_note = db.Column(db.Text, comment="Ghi chú nội bộ của nhà tuyển dụng")

    __table_args__ = (db.UniqueConstraint('candidate_id', 'job_id', name='_candidate_job_uc'),)


class Follow(BaseModel):  # Theo dõi công ty
    __tablename__ = 'follow'
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profile.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('candidate_id', 'company_id', name='_candidate_company_uc'),)


class CompanyReview(BaseModel):  # Đánh giá của ứng viên cho công ty
    __tablename__ = 'company_review'
    reviewer_id = db.Column(db.Integer, db.ForeignKey('candidate_profile.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1–5
    comment = db.Column(db.Text)


# --- VERIFICATION ---
class VerificationDocument(BaseModel):
    __tablename__ = 'verification_document'
    # Chỉ nhà tuyển dụng (công ty) mới cần xác thực
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False, unique=True)
    document_url = db.Column(db.String(255), nullable=False)  # file path or URL
    status = db.Column(db.Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING)
    admin_note = db.Column(db.Text)


class Payment(BaseModel):
    id = db.Column(db.Integer, db.ForeignKey('job_post.id', ondelete='CASCADE'), primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING, nullable=False)
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)

