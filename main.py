from datetime import datetime
from random import randrange

from flask import Flask, render_template, redirect, url_for, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional
import webbrowser
import os

from qiskit import Aer, execute

from qiskit_textbook.tools import simon_oracle
from qiskit.visualization import array_to_latex

from pauli_gate import add_x_gate, add_z_gate
from hadamard_gate import add_hadamard_gate
from cnot_gate import add_controlledX_gate
from draw_circuit import draw
from circuit import create_circuit
from histogram import create_histogram

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


class ButtonForm(FlaskForm):
    submit = SubmitField('Watch')

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


@app.route('/algorithms/Bernstein_Vazirani_algorithm', methods=['GET', 'POST'])
def bernsteinvazirani_algorithm_view():
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/files/berstein_vazirani_algorithm'
        if request.form['submit_button'] == 'Презентация':
            path = filepath + 'BVPresentation.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Упражнения':
            path = filepath + 'BVExercises.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Calculate':
            return redirect(
                url_for('bernstein_vazirani_algorithm')
            )
    return render_template(
        template_name_or_list='bernsteinvazirani_algorithm.html'
    )


@app.route('/algorithms/Grover_algorithm', methods=['GET', 'POST'])
def grover_algorithm_view():
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/files/grover_algorithm'
        if request.form['submit_button'] == 'Презентация':
            path = filepath + 'GPresentation.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Упражнения':
            path = filepath + 'GExercises.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Classical solution':
            return redirect(
                url_for('grover_classical_algorithm')
            )
        elif request.form['submit_button'] == 'Quantum solution':
            return redirect(
                url_for('grover_algorithm')
            )
    return render_template(
        template_name_or_list='grover_algorithm.html'
    )


@app.route('/algorithms/Quantum_Teleportation_algorithm', methods=['GET', 'POST'])
def quantumteleportation_algorithm_view():
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/files/quantum_teleportation_algorithm'
        if request.form['submit_button'] == 'Презентация':
            path = filepath + 'QTPresentation.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Упражнения':
            path = filepath + 'QTExercises.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Calculate':
            return redirect(
                url_for('quantum_teleportation_algorithm')
            )
    return render_template(
        template_name_or_list="quantumteleportation_algorithm.html"
    )

@app.route('/algorithms/Simon_algorithm', methods=['GET', 'POST'])
def simon_algorithm_view():
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/files/simon_algorithm'
        if request.form['submit_button'] == 'Презентация':
            path = filepath + 'SAPresentation.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Упражнения':
            path = filepath + 'SAExercises.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Classical solution':
            return redirect(
                url_for('simon_algorithm')
            )
    return render_template(
        template_name_or_list="simon_algorithm.html"
    )

# Bernstein Vazirani algorithm
@app.route('/algorithms/Bernstein_Vazirani_algorithm/quantum_solution', methods=['GET', 'POST'])
def bernstein_vazirani_algorithm():
    secret_number = '111000'
    num_qubits = len(secret_number) + 1
    num_bits = len(secret_number)
    circuit, quantum_register = create_circuit(
        num_qubits=num_qubits,
        num_bits=num_bits
    )
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=range(len(secret_number))
    )
    add_x_gate(
        circuit=circuit,
        qubit=len(secret_number)
    )
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[len(secret_number)]
    )
    circuit.barrier()
    for index, value in enumerate(reversed(secret_number)):
        if value == '1':
            add_controlledX_gate(
                circuit=circuit,
                quantum_register=quantum_register,
                vector_register=[index, len(secret_number)]
            )
    circuit.barrier()
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=range(len(secret_number))
    )
    circuit.barrier()
    circuit.measure(
        range(len(secret_number)),
        range(len(secret_number))
    )
    draw(
        circuit=circuit,
        filename="bernstein_vazirani_circuit"
    )
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(
        circuit,
        backend=simulator,
        shots=1
    ).result()
    counts = result.get_counts()
    create_histogram(
        counts=counts,
        name="bernstein_vazirani_algorithm_histogram"
    )
    print(counts)
    return render_template(
        template_name_or_list="bernsteinvazirani_algorithm.html"
    )


# Grover algorithm
@app.route('/algorithms/Grover_algorithm/quantum_solution', methods=['GET', 'POST'])
def grover_algorithm():
    num_qubits=2
    num_bits=2
    circuit, quantum_register = create_circuit(
        num_qubits=num_qubits,
        num_bits=num_bits
    )
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0,1]
    )
    # ORACLE
    add_z_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0,1]  
    )
    # DIFUSSION OPERATOR
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0,1]
    )
    circuit.z(
        [0,1]
    )
    add_z_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0,1]
    )
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0,1]
    )
    # EXPORT CIRCUIT
    draw(
        circuit=circuit,
        filename="grover_circuit"
    )
    # ANALYSIS
    sv_sim = Aer.get_backend('statevector_simulator')
    result = sv_sim.run(circuit).result()
    state_vector = result.get_statevector()
    result = array_to_latex(state_vector, prefix="|\\psi\\rangle =")

    circuit.measure_all()
    qasm_sim = Aer.get_backend('qasm_simulator')
    result = qasm_sim.run(circuit).result()
    counts = result.get_counts()
    create_histogram(
        counts=counts,
        name="grover_algorithm_histogram"
    )

    return render_template(
        template_name_or_list="grover_algorithm.html"
    )


@app.route('/algorithms/Grover_algorithm/classical_solution', methods=['GET'])
def grover_classical_algorithm():
    element_tofind = 7
    my_list = [1,3,5,2,4,9,5,8,0,7,6]
    def the_oracle(my_input):
        if my_input is element_tofind:
            response = True
        else:
            response = False
        return response
    
    for index, trial_number in enumerate(my_list):
        if the_oracle(trial_number):
            print('Winner found at index:', index)
            print('Calls to the Oracle used:', (index+1))
            break

    return render_template(
        template_name_or_list="grover_algorithm.html"
    )


# Quantum Teleportation algorithm
@app.route('/algorithms/Quantum_Teleportation_Algorithm/quantum_solution', methods=['GET', 'POST'])
def quantum_teleportation_algorithm():
    num_qubits = 3 # LABEL para la interfaz grafica
    num_bits = 3
    circuit, quantum_register = create_circuit(
        num_qubits=num_qubits,
        num_bits=num_bits
    )
    # Esto va en el label tambien
    #add_x_gate(
    #    circuit=circuit,
    #    qubit=0
    #)
    circuit.barrier()
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[1]
    )
    add_controlledX_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[1, 2]
    )
    add_controlledX_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0, 1]
    )
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0]
    )
    circuit.barrier()
    circuit.measure(
        [0,1],
        [0,1]
    )
    circuit.barrier()
    add_controlledX_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[1, 2]
    )
    add_z_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=[0, 2]
    )
    draw(
        circuit=circuit,
        filename="quantum_teleportation_circuit"
    )
    circuit.measure(2,2)
    simulator = Aer.get_backend('qasm_simulator')
    result = execute(
        circuit,
        backend=simulator,
        shots=1024
    ).result()
    counts = result.get_counts()
    create_histogram(
        counts=counts,
        name="quantum_teleportation_algorithm_histogram"
    )
    return render_template(
        template_name_or_list="quantumteleportation_algorithm.html"
    )

# Simon algorithm
@app.route('/algorithms/Simon_Algorithm/quantum_solution', methods=['GET', 'POST'])
def simon_algorithm():
    b = '110'
    n = len(b)
    circuit, quantum_register = create_circuit(
        num_qubits=n*2,
        num_bits=n
    )
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=range(n)
    )
    circuit.barrier()
    circuit = circuit.compose(simon_oracle(b))
    circuit.barrier()
    add_hadamard_gate(
        circuit=circuit,
        quantum_register=quantum_register,
        vector_register=range(n)
    )
    circuit.measure(
        range(n),
        range(n)
    )
    draw(
        circuit=circuit,
        filename="simon_circuit"
    )
    aer_sim = Aer.get_backend('aer_simulator')
    results = aer_sim.run(circuit).result()
    counts = results.get_counts()
    create_histogram(
        counts=counts,
        name="simon_algorithm_histogram"
    )
    for z in counts:
        print('{}.{} = {} (mod 2)'.format(b, z, bdotz(b,z)))
    return render_template(
        template_name_or_list="simon_algorithm.html"
    )

def bdotz(b, z):
    accum = 0
    for i in range(len(b)):
        accum += int(b[i]) * int(z[i])
    return (accum % 2)


# Обработчики ошибок (ERRORS)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


 # MAIN THREAD
if __name__ == '__main__':
    app.run()


# PARA GUARDAR LOS RESULTADOS DE LAS PRUEBAS EN PDF
# https://www.gitauharrison.com/articles/working-with-pdfs-in-flask

