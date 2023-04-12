from datetime import datetime
from random import randrange

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional


app = Flask(__name__)

# Подключается БД SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# Задаётся конкретное значение для конфигурационного ключа
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Всесто MY SECRET KEY придумайте и впишите свой ключ
app.config['SECRET_KEY'] = 'SECRET_KEY'

# В ORM передаётся в качестве параметра экземпляр приложения Flask
db = SQLAlchemy(app)


# MODELS

class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


# FORMS

class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название алгоритма',
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(1, 128)
        ]
    )
    text = TextAreaField(
        'Напишите мнение', 
        validators=[
            DataRequired(message='Обязательное поле')
        ]
    )
    source = URLField(
        'Добавьте ссылку на подробный обзор алгоритма',
        validators=[
            Length(1, 256),
            Optional()
        ]
    )
    submit = SubmitField('Добавить')


# FUNCTIONS

@app.route('/', methods=['GET'])
def index_view():
    quantity = Opinion.query.count()
    if not quantity:
        return 'В базе данных мнений о фильмах нет.'
    offset_value = randrange(quantity)
    opinion = Opinion.query.offset(offset_value).first()
    context = {
        'opinion': opinion
    }
    return render_template(
        template_name_or_list='opinion.html',
        **context
    )


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    form = OpinionForm()
    if form.validate_on_submit():
        opinion = Opinion(
            title=form.title.data,
            text=form.text.data,
            source=form.source.data
        )
        db.session.add(opinion)
        db.session.commit()
        return redirect(
            url_for('opinion_view',id=opinion.id)
        )
    context = {
        'form': form
    }
    return render_template(
        template_name_or_list='add_opinion.html',
        **context
    )


@app.route('/opinions/<int:id>', methods=['GET'])
def opinion_view(id):
    opinion = Opinion.query.get_or_404(id)
    context = {
        'opinion': opinion
    }
    return render_template(
        template_name_or_list='opinion.html',
        **context
    )

if __name__ == '__main__':
    app.run()