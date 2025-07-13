from random import choices

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from cloudinary.models import CloudinaryField

db = SQLAlchemy()

class RoleEnum(Enum):
    ADMIN = 'admin'
    RECRUITER = 'recruiter'
    CANDIDATE = 'candidate'

    CHOICES = [ADMIN, RECRUITER, CANDIDATE]

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    avatar = db.Column(db.String(255))

    # Relationships
    company = db.relationship("Company", uselist=False, backref="user")
    job_posts = db.relationship("JobPost", backref="recruiter", lazy=True, foreign_keys='JobPost.recruiter_id')
    applications = db.relationship("Application", backref="applicant", lazy=True, foreign_keys='Application.applicant_id')
    given_reviews = db.relationship("Review", backref="reviewer", lazy=True, foreign_keys='Review.reviewer_id')
    received_reviews = db.relationship("Review", backref="reviewed_user", lazy=True, foreign_keys='Review.reviewed_user_id')
    verification_document = db.relationship("VerificationDocument", uselist=False, backref="user")

#Công ty doanh nghiệp
class Company(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    tax_code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)

    images = db.relationship("CompanyImage", backref="company", lazy=True)

#Ảnh Công ty doanh nghiệp
class CompanyImage(BaseModel):
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    image = db.Column(db.String(255))  # URL Cloudinary

#Tin tuyển dụng
class JobPost(BaseModel):
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    specialized = db.Column(db.String(100), default="Chưa phân loại")
    description = db.Column(db.Text)
    salary = db.Column(db.Numeric(10, 2))
    working_hours = db.Column(db.String(50))
    location = db.Column(db.String(255))

    applications = db.relationship("Application", backref="job", lazy=True)

#Đơn ứng tuyển
class Application(BaseModel):
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.id'), nullable=False)
    cv = db.Column(db.String(255))  # URL Cloudinary
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected

    __table_args__ = (db.UniqueConstraint('applicant_id', 'job_id', name='_applicant_job_uc'),)

#Theo dõi nhà tuyển dụng
class Follow(BaseModel):
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('follower_id', 'recruiter_id', name='_follower_recruiter_uc'),)

#Đánh giá
class Review(BaseModel):
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer)  # 1–5
    comment = db.Column(db.Text)

#Trạng thái xác minh
class VerificationStatusEnum(Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

#Giấy tờ xác thực
class VerificationDocument(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    document = db.Column(db.String(255))  # file path or URL
    status = db.Column(db.Enum(VerificationStatusEnum), default=VerificationStatusEnum.pending)
    admin_note = db.Column(db.Text, nullable=True)