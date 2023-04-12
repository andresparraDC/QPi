from datetime import datetime
from random import randrange

from flask import Flask, render_template, redirect, url_for, abort
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
        #return 'В базе данных мнений о фильмах нет.'
        abort(404)
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

# ALGORITHMS

@app.route('/algorithms', methods=['GET'])
def index_algorithms_view():
    return render_template(
        template_name_or_list='index_algorithms.html'
    )


@app.route('/algorithms/Bernstein_Vazirani_algorithm', methods=['GET'])
def bernsteinvazirani_algorithm_view():
    return render_template(
        template_name_or_list='bernsteinvazirani_algorithm.html'
    )


@app.route('/algorithms/Grover_algorithm', methods=['GET'])
def grover_algorithm_view():
    return render_template(
        template_name_or_list='grover_algorithm.html'
    )


@app.route('/algorithms/Quantum_Teleportation_algorithm', methods=['GET'])
def quantumteleportation_algorithm_view():
    return render_template(
        template_name_or_list='quantumteleportation_algorithm.html'
    )


@app.route('/algorithms/Simon_algorithm', methods=['GET'])
def simon_algorithm_view():
    return render_template(
        template_name_or_list='simon_algorithm.html'
    )

# Обработчики ошибок (ERRORS)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


 # THREAD MAIN
if __name__ == '__main__':
    app.run()
