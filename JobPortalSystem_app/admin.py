# admin.py
from flask import redirect, url_for, flash
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import func
from datetime import datetime

from .models import RoleEnum, db, User, Company, JobPost, CandidateProfile, Application, \
    JobTypeEnum, ExperienceLevelEnum, ApplicationStatusEnum, PaymentStatusEnum, Payment
from wtforms.fields import TextAreaField, SelectField
from wtforms.validators import URL, Optional, DataRequired


# --- CÁC HÀM FORMATTER ---
def _boolean_formatter(view, context, model, name):
    """Hiển thị icon check/cross cho các giá trị boolean."""
    value = getattr(model, name)
    if value:
        return Markup('<span class="fa fa-check-circle text-success"></span>')
    else:
        return Markup('<span class="fa fa-times-circle text-danger"></span>')

def _description_formatter(view, context, model, name):
    """Rút gọn văn bản dài."""
    value = getattr(model, name)
    if value and len(value) > 50:
        return value[:50] + '...'
    return value

def _company_link_formatter(view, context, model, name):
    """Tạo link đến trang chỉnh sửa công ty."""
    if not model.company:
        return ""
    url = url_for('company-admin.edit_view', id=model.company.id)
    return Markup(f'<a href="{url}">{model.company.name}</a>')

# --- VIEW TRANG CHỦ ADMIN ---
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        revenue_by_month = (
            db.session.query(
                func.DATE_FORMAT(Payment.created_date, '%Y-%m').label('month'),
                func.sum(Payment.amount).label('total_revenue')
            )
            .filter(Payment.status == PaymentStatusEnum.COMPLETED)
            .filter(Payment.created_date.isnot(None))
            .group_by('month')
            .order_by('month')
            .all()
        )

        chart_labels = [datetime.strptime(row.month, '%Y-%m').strftime('Tháng %m/%Y') for row in revenue_by_month]
        chart_data = [float(row.total_revenue) for row in revenue_by_month]

        return self.render('admin/dashboard.html', chart_labels=chart_labels, chart_data=chart_data)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == RoleEnum.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.home'))

# --- VIEW MODEL BẢO MẬT ---
class SecuredModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == RoleEnum.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.home'))


class UserAdminView(SecuredModelView):
    column_list = ['id', 'username', 'email', 'role', 'active']
    column_searchable_list = ['username', 'email']
    column_filters = ['role', 'active']
    column_formatters = {'active': _boolean_formatter}
    form_columns = ['username', 'email', 'role', 'active']
    column_labels = {'username': 'Tên đăng nhập', 'email': 'Email', 'role': 'Vai trò', 'active': 'Hoạt động'}

    form_overrides = {
        'role': SelectField
    }
    form_args = {
        'role': {
            'choices': [(e.name, e.value) for e in RoleEnum],
            'coerce': RoleEnum
        }
    }

class CompanyAdminView(SecuredModelView):
    column_select_related = ['user']

    column_list = ['name', 'user.username', 'location', 'is_verified', 'active']
    column_searchable_list = ['name', 'location', 'user.username']
    column_filters = ['is_verified', 'active']
    # FIX: Sử dụng cú pháp an toàn {} cho dictionary keys có chứa dấu chấm.
    column_labels = {
        'name': 'Tên công ty',
        'user.username': 'Tài khoản Recruiter',
        'location': 'Địa chỉ',
        'is_verified': 'Đã xác thực',
        'active': 'Hoạt động'
    }
    column_formatters = {
        'is_verified': _boolean_formatter,
        'active': _boolean_formatter,
        'description': _description_formatter
    }
    form_columns = ['name', 'user', 'tax_code', 'description', 'location', 'website', 'is_verified', 'active']
    form_overrides = {
        'description': TextAreaField
    }
    form_args = {
        'description': {'render_kw': {'rows': 10, 'style': 'width: 100%;'}},
        'website': {'validators': [Optional(), URL(message="Vui lòng nhập một URL hợp lệ.")]}
    }

    @action('verify_companies', 'Xác thực Công ty', 'Bạn có chắc muốn xác thực các công ty đã chọn?')
    def action_verify(self, ids):
        try:
            companies_to_verify = Company.query.filter(Company.id.in_(ids)).all()
            count = 0
            for company in companies_to_verify:
                if not company.is_verified:
                    company.is_verified = True
                    count += 1
            db.session.commit()
            flash(f'Đã xác thực thành công {count} công ty.', 'success')
        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash(f'Lỗi khi xác thực công ty: {e}', 'error')


class JobPostAdminView(SecuredModelView):
    column_select_related = ['company']
    column_list = ['title', 'company', 'location', 'job_type', 'experience_level', 'active']
    column_searchable_list = ['title', 'location', 'company.name']
    column_filters = ['job_type', 'experience_level', 'active']
    column_labels = {
        'title': 'Chức danh',
        'company': 'Công ty',
        'location': 'Địa điểm',
        'job_type': 'Loại hình',
        'experience_level': 'Cấp bậc',
        'active': 'Hiển thị'
    }
    column_formatters = {
        'active': _boolean_formatter,
        'company': _company_link_formatter
    }
    can_create = False
    can_edit = True
    can_delete = True
    form_columns = [
        'title', 'company', 'location', 'description',
        'job_type', 'experience_level', 'active'
    ]
    form_overrides = {
        'job_type': SelectField,
        'experience_level': SelectField
    }
    form_args = {
        'job_type': {
            'choices': [(e.name, e.value) for e in JobTypeEnum],
            'coerce': JobTypeEnum
        },
        'experience_level': {
            'choices': [(e.name, e.value) for e in ExperienceLevelEnum],
            'coerce': ExperienceLevelEnum
        }
    }

class ApplicationAdminView(SecuredModelView):
    column_select_related = ['job', 'candidate']
    can_edit = True
    can_create = False
    can_delete = True
    form_columns = ['status']
    column_list = ['job.title', 'candidate.full_name', 'status', 'created_date']
    column_searchable_list = ['job.title', 'candidate.full_name']
    column_filters = ['status', 'created_date']
    # FIX: Sử dụng cú pháp an toàn {} cho dictionary keys có chứa dấu chấm.
    column_labels = {
        'job.title': 'Tên công việc',
        'candidate.full_name': 'Ứng viên',
        'status': 'Trạng thái',
        'created_date': 'Ngày nộp'
    }
    form_overrides = {
        'status': SelectField
    }
    form_args = {
        'status': {
            'choices': [(e.name, e.value) for e in ApplicationStatusEnum],
            'coerce': ApplicationStatusEnum
        }
    }

class PaymentAdminView(SecuredModelView):
    column_select_related = ['job_post']
    can_edit = True
    can_create = False
    can_delete = False
    form_columns = ['status']
    column_list = ['job_post.title', 'amount', 'status', 'payment_date', 'transaction_id']
    column_filters = ['status', 'payment_date']
    column_searchable_list = ['job_post.title', 'transaction_id']
    # FIX: Sử dụng cú pháp an toàn {} cho dictionary keys có chứa dấu chấm.
    column_labels = {
        'job_post.title': 'Tin đăng',
        'amount': 'Số tiền',
        'status': 'Trạng thái',
        'payment_date': 'Ngày thanh toán',
        'transaction_id': 'Mã giao dịch MoMo'
    }
    form_overrides = {
        'status': SelectField
    }
    form_args = {
        'status': {
            'label': 'Trạng thái',
            'validators': [DataRequired()],  # Đảm bảo đây là một list
            'choices': [(item.name, item.value) for item in PaymentStatusEnum],
            'coerce': PaymentStatusEnum
        }
    }

# --- KHỞI TẠO VÀ GẮN VIEW ---
def setup_admin(app):
    admin = Admin(app, name="Job Portal Dashboard", template_mode="bootstrap4", index_view=MyAdminIndexView())

    admin.add_view(
        UserAdminView(User, db.session, name="Người dùng", category="Quản lý Tài khoản", endpoint='user-admin'))
    admin.add_view(
        CompanyAdminView(Company, db.session, name="Công ty", category="Quản lý Tài khoản", endpoint='company-admin'))
    admin.add_view(SecuredModelView(CandidateProfile, db.session, name="Hồ sơ ứng viên", category="Quản lý Tài khoản",
                                    endpoint='candidate-profile-admin'))
    admin.add_view(JobPostAdminView(JobPost, db.session, name="Tin tuyển dụng", category="Quản lý Tuyển dụng",
                                    endpoint='job-post-admin'))
    admin.add_view(ApplicationAdminView(Application, db.session, name="Lượt ứng tuyển", category="Quản lý Tuyển dụng",
                                    endpoint='application-admin'))
    admin.add_view(PaymentAdminView(Payment, db.session, name="Thanh toán", category="Quản lý Tài chính", endpoint='payment-admin'))

    return admin