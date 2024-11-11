from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField 
from wtforms.validators import DataRequired, Length
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define the Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))


# Define the form for creating an item
class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description = StringField('Description', validators=[Length(max=100)])
    submit = SubmitField('Create Item')


@app.route('/')
def index(): 
    items = Item.query.all() 
    flash('Welcome to the Item Management System!', 'success')  # Flash message 
    return render_template('index.html', items=items)


@app.route('/create_item', methods=['GET', 'POST'])
def create_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, description=form.description.data)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('item_created'))
    return render_template('create_item.html', form=form)


@app.route('/item_created')
def item_created():
    return "Item created successfully!"


def create_db_and_sample_data(): 
    with app.app_context(): 
        db.create_all()    # Sample data 
        sample_items = [ 
            Item(name='Sample Item 1', description='Description for sample item 1'), 
            Item(name='Sample Item 2', description='Description for sample item 2'), 
            Item(name='Sample Item 3', description='Description for sample item 3'), ] 
        db.session.bulk_save_objects(sample_items) 
        db.session.commit() 
        print("Database initialized with sample data.")


if __name__ == "__main__": 
    # Uncomment the line below to create the database and sample data
    # create_db_and_sample_data()
    app.run(debug=True)
