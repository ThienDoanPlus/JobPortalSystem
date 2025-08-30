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
    JobTypeEnum, ExperienceLevelEnum, ApplicationStatusEnum, PaymentStatusEnum, Payment  # Import thêm User và RoleEnum
from wtforms.fields import TextAreaField, SelectField
from wtforms.validators import URL, Optional


# --- CÁC HÀM FORMATTER ---
def _boolean_formatter(view, context, model, name):
    """Hiển thị icon check/cross cho các giá trị boolean."""
    value = getattr(model, name)
    if value:
        # Trả về mã HTML cho icon check màu xanh
        return Markup('<span class="fa fa-check-circle text-success"></span>')
    else:
        # Trả về mã HTML cho icon cross màu đỏ
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
    # Tạo URL đến trang edit view của CompanyAdminView
    # Endpoint được lấy từ endpoint='company-admin' mà chúng ta đã định nghĩa
    url = url_for('company-admin.edit_view', id=model.company.id)
    return Markup(f'<a href="{url}">{model.company.name}</a>')
# Tạo một class tùy chỉnh để bảo vệ trang admin chính
class MyAdminIndexView(AdminIndexView):
    @expose('/')  # Sử dụng decorator @expose để định nghĩa route cho trang chủ admin
    def index(self):
        revenue_by_month = (
            db.session.query(
                # Sửa thành func.DATE_FORMAT với cú pháp của MySQL
                func.DATE_FORMAT(Payment.created_date, '%Y-%m').label('month'),
                func.sum(Payment.amount).label('total_revenue')
            )
            .filter(Payment.status == PaymentStatusEnum.COMPLETED)
            .group_by('month')
            .order_by('month')
            .all()
        )


        # Xử lý dữ liệu để truyền sang template
        chart_labels = [datetime.strptime(row.month, '%Y-%m').strftime('Tháng %m/%Y') for row in revenue_by_month]
        chart_data = [float(row.total_revenue) for row in revenue_by_month]

        # Truyền dữ liệu vào template
        return self.render('admin/dashboard.html', chart_labels=chart_labels, chart_data=chart_data)

    def is_accessible(self):
        # Chỉ trả về True nếu user đã đăng nhập VÀ có vai trò là ADMIN
        return current_user.is_authenticated and current_user.role == RoleEnum.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        # Chuyển hướng về trang chủ nếu không có quyền
        return redirect(url_for('main.home'))

# Tạo một class ModelView tùy chỉnh để bảo vệ các trang quản lý model
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

    # Chỉ định các cột sẽ hiển thị trên form
    form_columns = ['username', 'email', 'role', 'active']

    column_labels = dict(username='Tên đăng nhập', email='Email', role='Vai trò', active='Hoạt động')

    # --- BẮT ĐẦU SỬA LỖI TẠI ĐÂY ---
    # Ghi đè, yêu cầu dùng SelectField cho trường 'role'
    form_overrides = {
        'role': SelectField
    }

    # Cung cấp danh sách lựa chọn và cách xử lý cho SelectField 'role'
    form_args = {
        'role': {
            'choices': [(e.name, e.value) for e in RoleEnum],  # Tạo choices từ RoleEnum
            'coerce': RoleEnum  # Ép kiểu chuỗi trả về thành đối tượng RoleEnum
        }
    }

class CompanyAdminView(SecuredModelView):
    column_list = ['name', 'user.username', 'location', 'is_verified', 'active']
    column_searchable_list = ['name', 'location']
    column_filters = ['is_verified', 'active']
    # Đặt lại tên cột cho dễ hiểu
    column_labels = dict(name='Tên công ty', user_username='Tài khoản Recruiter', location='Địa chỉ', is_verified='Đã xác thực', active='Hoạt động')
    column_formatters = {
        'is_verified': _boolean_formatter,
        'active': _boolean_formatter,
        'description': _description_formatter
    }
    # Cho phép chỉnh sửa các trường này
    form_columns = ['name', 'tax_code', 'description', 'location', 'website', 'is_verified', 'active']

    # Biến trường description thành một textarea lớn hơn
    form_overrides = dict(description=TextAreaField)
    form_args = dict(
        description=dict(render_kw={'rows': 10, 'style': 'width: 100%;'}),
        website=dict(validators=[Optional(), URL(message="Vui lòng nhập một URL hợp lệ.")])
    )

    # ĐỊNH NGHĨA ACTION
    @action('verify_companies', 'Xác thực Công ty', 'Bạn có chắc muốn xác thực các công ty đã chọn?')
    def action_verify(self, ids):
        try:
            # Lấy danh sách các công ty dựa trên id đã chọn
            companies_to_verify = Company.query.filter(Company.id.in_(ids)).all()

            count = 0
            for company in companies_to_verify:
                company.is_verified = True
                count += 1

            db.session.commit()

            flash(f'Đã xác thực thành công {count} công ty.', 'success')
        except Exception as e:
            if not self.handle_view_exception(e):
                raise
            flash(f'Lỗi khi xác thực công ty: {e}', 'error')


class JobPostAdminView(SecuredModelView):
    # --- BẮT ĐẦU SỬA LỖI VÀ TỐI ƯU ---
    # 1. Thêm column_select_related để tối ưu hóa truy vấn và giúp tìm kiếm
    column_select_related = ['company']

    # 2. Quay lại dùng cú pháp 'relationship.field' đơn giản
    column_searchable_list = ['title', 'location', 'company.name']
    # --- KẾT THÚC SỬA LỖI ---

    # Giữ nguyên các phần còn lại đã hoạt động tốt
    column_list = ['title', 'company', 'location', 'job_type', 'experience_level', 'active']
    column_filters = ['job_type', 'experience_level', 'active']
    column_labels = dict(title='Chức danh', company='Công ty', location='Địa điểm', job_type='Loại hình',
                         experience_level='Cấp bậc', active='Hiển thị')

    column_formatters = {
        'active': _boolean_formatter,
        'company': _company_link_formatter
    }

    can_create = False
    can_edit = True
    can_delete = True

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

# Tạo class mới này, có thể đặt nó sau JobPostAdminView
class ApplicationAdminView(SecuredModelView):
    # Chỉ cho phép xem và xóa, không cho chỉnh sửa trực tiếp để tránh sai sót logic
    can_edit = False
    can_create = False
    can_delete = True

    column_list = ['job.title', 'candidate.full_name', 'status', 'created_date']
    column_filters = ['status']
    column_labels = dict(job_title='Tên công việc', candidate_full_name='Ứng viên', status='Trạng thái', created_date='Ngày nộp')

    # --- SỬA LỖI EDIT TẠI ĐÂY ---
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
    can_create = False
    can_edit = False
    can_delete = False
    column_list = ['job_post.title', 'amount', 'status', 'payment_date', 'transaction_id']
    column_filters = ['status', 'payment_date']
    column_labels = dict(job_post_title='Tin đăng', amount='Số tiền', status='Trạng thái', payment_date='Ngày thanh toán', transaction_id='Mã giao dịch MoMo')

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

    return admin