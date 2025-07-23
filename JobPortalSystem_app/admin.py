from flask import app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
admin = Admin (app, name="Job Portal System", template_mode="bootstrap4")
