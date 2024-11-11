from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_migrate import Migrate
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# Initialize Flask-Admin
admin = Admin(app, name='StudentAdmin', template_mode='bootstrap3')


# Define the User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Define the Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)


# Add models to Flask-Admin
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3)])


class UserAdmin(ModelView):
    column_exclude_list = ('password_hash',)  # Exclude the password hash from the view
    form = UserForm  # Use the custom form for creating/updating users
    
    def is_accessible(self):
        # Only allow access if the user is authenticated and an admin
        return current_user.is_authenticated and current_user.role == 'admin'

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

    def delete_model(self, model):
        # Only allow admins to delete users
        if not (current_user.role == 'admin'):
            flash('You do not have permission to delete users.', 'danger')
            return redirect(url_for('index'))
        return super().delete_model(model)


# Define the form for creating and updating a student
class StudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    submit = SubmitField('Submit')


class StudentAdmin(ModelView):
    form = StudentForm  # Use the form for creating/updating students

    def is_accessible(self):
        # Only allow access if the user is authenticated and an admin
        return current_user.is_authenticated and current_user.role == 'admin'

    def delete_model(self, model):
        # Only allow admins to delete students
        if not (current_user.role == 'admin'):
            flash('You do not have permission to delete students.', 'danger')
            return redirect(url_for('index'))
        return super().delete_model(model)


# Define the form for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3)])
    submit = SubmitField('Login')


admin.add_view(StudentAdmin(Student, db.session))  # Use the StudentAdmin view for students
admin.add_view(UserAdmin(User, db.session)) 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create_student', methods=['GET', 'POST'])
def create_student():
    if not current_user.is_authenticated or not (current_user.role == 'admin'):
        flash('You do not have permission to create students.', 'danger')
        return redirect(url_for('index'))  # Redirect non-admins to the main page
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(first_name=form.first_name.data, last_name=form.last_name.data, age=form.age.data)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_student.html', form=form)


@app.route('/update_student/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if not current_user.is_authenticated or not (current_user.role == 'admin'):
        flash('You do not have permission to update students.', 'danger')
        return redirect(url_for('index'))  # Redirect non-admins to the main page
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.age = form.age.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_student.html', form=form)


@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    if not current_user.is_authenticated or not (current_user.role == 'admin'):
        flash('You do not have permission to delete students.', 'danger')
        return redirect(url_for('index'))  # Redirect non-admins to the main page
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
