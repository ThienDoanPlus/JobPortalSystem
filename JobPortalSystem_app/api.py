# /JobPortalSystem/JobPortalSystem_app/api.py

from flask import Blueprint, jsonify, request, current_app, url_for
from flask_login import login_required, current_user

from . import db, dao
from .models import RoleEnum, Application, JobPost, Company, Experience, Education, Skill

api_bp = Blueprint('api', __name__, url_prefix='/api')


# --- API cho Dashboard Ứng viên ---

@api_bp.route('/candidate/applied-jobs', methods=['GET'])
@login_required
def get_applied_jobs():
    """Lấy danh sách các công việc mà ứng viên đã ứng tuyển."""
    try:
        # 1. Kiểm tra role
        if current_user.role != RoleEnum.CANDIDATE:
            return jsonify({'error': 'Permission denied'}), 403

        # 2. Kiểm tra candidate profile
        if not hasattr(current_user, 'candidate_profile') or not current_user.candidate_profile:
            return jsonify([])  # Trả về danh sách rỗng nếu không có profile

        # 3. Truy vấn dữ liệu
        applications = (
            db.session.query(Application, JobPost, Company)
            .join(JobPost, Application.job_id == JobPost.id)
            .join(Company, JobPost.company_id == Company.id)
            .filter(
                Application.candidate_id == current_user.candidate_profile.id,
                JobPost.active == True  # Chỉ lấy job đang hoạt động
            )
            .order_by(Application.created_date.desc())
            .all()
        )

        # 4. Build response
        result = []
        for app, job, company in applications:
            if not all([app, job, company]):  # Bỏ qua nếu có bất kỳ record nào null
                continue
            if company.images:
                logo_url = company.images[0].image_url

            result.append({
                'application_id': app.id,
                'job_id': job.id,
                'job_title': job.title,
                'company_name': company.name,
                'company_logo': logo_url,
                'status': app.status.value if app.status else None,
                'applied_date': app.created_date.strftime('%d/%m/%Y') if app.created_date else None
            })

        return jsonify(result)

    except Exception as e:
        current_app.logger.error(f"Error in get_applied_jobs: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


# --- API cho CV (full update, layout, style) ---

@api_bp.route('/cv/<int:cv_id>', methods=['PUT'])
@login_required
def update_full_cv(cv_id):
    """Cập nhật toàn bộ CV (autosave)."""
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    try:
        cv.title = data.get('title', cv.title)

        if 'style' in data:
            cv.font_family = data['style'].get('font_family', cv.font_family)
            cv.theme_color = data['style'].get('theme_color', cv.theme_color)

        if 'candidate_profile' in data and cv.candidate:
            profile_data = data['candidate_profile']
            cv.candidate.full_name = profile_data.get('full_name', cv.candidate.full_name)
            cv.candidate.phone_number = profile_data.get('phone_number', cv.candidate.phone_number)

        db.session.commit()
        return jsonify({'success': True, 'message': 'CV updated successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Lỗi khi cập nhật toàn bộ CV: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/cv/<int:cv_id>/layout', methods=['PUT'])
@login_required
def update_cv_layout(cv_id):
    """Cập nhật layout CV."""
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    try:
        cv.layout = data.get('layout', cv.layout)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Layout updated'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Lỗi khi cập nhật layout: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/cv/<int:cv_id>/style', methods=['PUT'])
@login_required
def update_cv_style(cv_id):
    """Cập nhật style CV."""
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    try:
        cv.font_family = data.get('font_family', cv.font_family)
        cv.theme_color = data.get('theme_color', cv.theme_color)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Style updated'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Lỗi khi cập nhật style: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# --- Candidate profile ---

@api_bp.route('/candidate/profile', methods=['PUT'])
@login_required
def update_candidate_profile():
    """Cập nhật thông tin cá nhân của ứng viên."""
    if current_user.role != RoleEnum.CANDIDATE:
        return jsonify({'error': 'Permission denied'}), 403

    profile = current_user.candidate_profile
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    data = request.json
    if not data:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        profile.full_name = data.get('full_name', profile.full_name)
        profile.phone_number = data.get('phone_number', profile.phone_number)
        profile.address = data.get('address', profile.address)
        profile.linkedin_url = data.get('linkedin_url', profile.linkedin_url)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Lỗi khi cập nhật profile: {e}")
        return jsonify({'error': 'Internal server error'}), 500


# --- Lấy dữ liệu CV ---

@api_bp.route('/cv/<int:cv_id>', methods=['GET'])
@login_required
def get_cv_data(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    if not current_user.candidate_profile:
        return jsonify({'error': 'User has no candidate profile'}), 403

    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Not found or permission denied'}), 404

    profile = cv.candidate

    experiences = [
        {
            'id': e.id,
            'job_title': e.job_title,
            'company_name': e.company_name,
            'description': e.description,
            'order': e.order
        }
        for e in cv.experiences
    ]
    educations = [
        {
            'id': e.id,
            'institution_name': e.institution_name,
            'degree': e.degree,
            'major': e.major,
            'order': e.order
        }
        for e in cv.educations
    ]
    skills = [{'id': s.id, 'skill_name': s.skill_name} for s in cv.skills]

    return jsonify({
        'id': cv.id,
        'title': cv.title,
        'candidate_profile': {
            'full_name': profile.full_name,
            'email': profile.user.email,
            'phone_number': profile.phone_number,
            'address': profile.address,
            'linkedin_url': profile.linkedin_url
        },
        'style': {
            'font_family': cv.font_family,
            'font_size': cv.font_size,
            'line_spacing': cv.line_spacing,
            'theme_color': cv.theme_color,
            'background_style': cv.background_style,
        },
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
    })


# --- API cho mục Kinh nghiệm ---

@api_bp.route('/cv/<int:cv_id>/experience', methods=['POST'])
@login_required
def add_experience(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    new_exp = Experience(
        resume_id=cv.id,
        job_title="Chức danh mới",
        company_name="Tên công ty",
        description="Mô tả công việc của bạn..."
    )
    db.session.add(new_exp)
    db.session.commit()

    return jsonify({
        'id': new_exp.id,
        'job_title': new_exp.job_title,
        'company_name': new_exp.company_name,
        'description': new_exp.description,
        'order': new_exp.order
    }), 201


@api_bp.route('/experience/<int:exp_id>', methods=['PUT'])
@login_required
def update_experience(exp_id):
    exp = Experience.query.get(exp_id)
    if not exp or exp.resume.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    exp.job_title = data.get('job_title', exp.job_title)
    exp.company_name = data.get('company_name', exp.company_name)
    exp.description = data.get('description', exp.description)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Experience updated'})


@api_bp.route('/experience/<int:exp_id>', methods=['DELETE'])
@login_required
def delete_experience(exp_id):
    exp = Experience.query.get(exp_id)
    if not exp or exp.resume.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    db.session.delete(exp)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Experience deleted'})


# --- API cho mục Học vấn ---

@api_bp.route('/cv/<int:cv_id>/education', methods=['POST'])
@login_required
def add_education(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    new_edu = Education(
        resume_id=cv.id,
        institution_name="Tên trường",
        degree="Bằng cấp",
        major="Chuyên ngành"
    )
    db.session.add(new_edu)
    db.session.commit()

    return jsonify({
        'id': new_edu.id,
        'institution_name': new_edu.institution_name,
        'degree': new_edu.degree,
        'major': new_edu.major,
        'order': new_edu.order
    }), 201


@api_bp.route('/education/<int:edu_id>', methods=['PUT'])
@login_required
def update_education(edu_id):
    edu = Education.query.get_or_404(edu_id)
    if edu.resume.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    edu.institution_name = data.get('institution_name', edu.institution_name)
    edu.degree = data.get('degree', edu.degree)
    edu.major = data.get('major', edu.major)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Education updated'})


@api_bp.route('/education/<int:edu_id>', methods=['DELETE'])
@login_required
def delete_education(edu_id):
    edu = Education.query.get_or_404(edu_id)
    if edu.resume.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    db.session.delete(edu)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Education deleted'})


# --- API cho mục Kỹ năng ---

@api_bp.route('/cv/<int:cv_id>/skill', methods=['POST'])
@login_required
def add_skill(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    skill_name = data.get('skill_name', 'Kỹ năng mới')

    new_skill = Skill(resume_id=cv.id, skill_name=skill_name)
    db.session.add(new_skill)
    db.session.commit()

    return jsonify({'id': new_skill.id, 'skill_name': new_skill.skill_name}), 201


@api_bp.route('/skill/<int:skill_id>', methods=['PUT'])
@login_required
def update_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.resume.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    skill.skill_name = data.get('skill_name', skill.skill_name)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Skill updated'})


@api_bp.route('/skill/<int:skill_id>', methods=['DELETE'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.resume.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    db.session.delete(skill)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Skill deleted'})


# --- API reorder (Experience, Education, Skill) ---

@api_bp.route('/cv/<int:cv_id>/<string:section>/reorder', methods=['PUT'])
@login_required
def reorder_section_items(cv_id, section):
    cv = dao.get_cv_by_id(cv_id)
    if not cv or cv.candidate_id != current_user.candidate_profile.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.json
    item_ids_in_order = data.get('ids', [])

    model_map = {
        'experiences': Experience,
        'experience': Experience,
        'educations': Education,
        'education': Education,
        'skills': Skill,
        'skill': Skill,
    }
    ModelClass = model_map.get(section)
    if not ModelClass:
        return jsonify({'error': 'Invalid section'}), 400

    try:
        for index, item_id in enumerate(item_ids_in_order):
            item = ModelClass.query.get(item_id)
            if item and item.resume_id == cv_id:
                item.order = index
        db.session.commit()
        return jsonify({'success': True, 'message': 'Order updated'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Lỗi khi reorder {section}: {e}")
        return jsonify({'error': 'Internal server error'}), 500
