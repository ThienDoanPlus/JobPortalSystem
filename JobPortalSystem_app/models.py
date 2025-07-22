from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum


db = SQLAlchemy()

class RoleEnum(Enum):
    ADMIN = 'admin'
    RECRUITER = 'recruiter'
    CANDIDATE = 'candidate'

class VerificationStatusEnum(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class PaymentStatusEnum(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(BaseModel):
    __tablename__ = 'user'

    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(RoleEnum), nullable=False)
    avatar = db.Column(db.String(255))

    admin = db.relationship("Admin", uselist=False, backref="user")
    recruiter = db.relationship("Recruiter", uselist=False, backref="user")
    candidate = db.relationship("Candidate", uselist=False, backref="user")

class Admin(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

class Company(BaseModel):
    name = db.Column(db.String(255), nullable=False)
    tax_code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)

    images = db.relationship("CompanyImage", backref="company", lazy=True)
    recruiters = db.relationship("Recruiter", backref="company", lazy=True)
    followers = db.relationship("Follow", backref="company", lazy=True)
    reviews = db.relationship("Review", backref="company", lazy=True)

class CompanyImage(BaseModel):
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    image = db.Column(db.String(255))

class Recruiter(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    job_posts = db.relationship("JobPost", backref="recruiter", lazy=True)
    verification_documents = db.relationship("VerificationDocument", backref="recruiter", lazy=True)

class Candidate(BaseModel):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    applications = db.relationship("Application", backref="candidate", lazy=True)
    follows = db.relationship("Follow", backref="candidate", lazy=True)
    reviews = db.relationship("Review", backref="candidate", lazy=True)

class VerificationDocument(BaseModel):
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'), nullable=False)
    document = db.Column(db.String(255))
    status = db.Column(db.Enum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING)
    admin_note = db.Column(db.Text)

class JobPost(BaseModel):
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    specialized = db.Column(db.String(100), default="Chưa phân loại")
    description = db.Column(db.Text)
    salary = db.Column(db.Numeric(10, 2))
    working_hours = db.Column(db.String(50))
    location = db.Column(db.String(255))

    applications = db.relationship("Application", backref="job_post", lazy=True)
    payment = db.relationship("Payment", backref="job_post", uselist=False, lazy=True, cascade="all, delete-orphan", primaryjoin="JobPost.id == Payment.id")

class Payment(BaseModel):
    id = db.Column(db.Integer, db.ForeignKey('job_post.id', ondelete='CASCADE'), primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.Enum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING, nullable=False)
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)

class Application(BaseModel):
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    job_post_id = db.Column(db.Integer, db.ForeignKey('job_post.id'), nullable=False)
    cv = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')

    __table_args__ = (db.UniqueConstraint('candidate_id', 'job_post_id', name='_candidate_job_uc'),)

class Follow(BaseModel):
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('candidate_id', 'company_id', name='_candidate_company_uc'),)

class Review(BaseModel):
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('candidate_id', 'company_id', name='_candidate_review_uc'),)