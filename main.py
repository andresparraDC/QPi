import os
import warnings
import webbrowser
from datetime import datetime
from random import randrange

import matplotlib.pyplot as plot
import numpy as np
from flask import Flask, abort, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from IPython.display import display
from qiskit import (Aer, ClassicalRegister, QuantumCircuit, QuantumRegister,
                    execute, transpile)
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from qiskit.visualization import array_to_latex, plot_bloch_multivector
from qiskit_textbook.tools import simon_oracle
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

warnings.filterwarnings('ignore')

from circuit import create_circuit
from cnot_gate import add_controlledX_gate
from draw_circuit import draw, draw_sudoku_example
from hadamard_gate import add_hadamard_gate
from histogram import create_histogram, create_sudoku_histogram
from pauli_gate import add_x_gate, add_z_gate


# CONFIGURATION APP
# ___________________________________________________________________________
app = Flask(__name__)

# Подключается БД SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# Задаётся конкретное значение для конфигурационного ключа
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Всесто MY SECRET KEY придумайте и впишите свой ключ
app.config['SECRET_KEY'] = 'SECRET_KEY'

# В ORM передаётся в качестве параметра экземпляр приложения Flask
db = SQLAlchemy(app)

FORMAT_TIME = '%Y-%m-%d-Time-%H-%M-%S' 
NOW_TIME = datetime.strftime(datetime.now(), FORMAT_TIME) 


# MODELS
# ___________________________________________________________________________
class Opinion(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    title = db.Column(
        db.String(128),
        nullable=False
    )
    text = db.Column(
        db.Text,
        unique=True,
        nullable=False
    )
    source = db.Column(
        db.String(256)
    )
    timestamp = db.Column(
        db.DateTime,
        index=True,
        default=datetime.utcnow
    )


# FORMS
# ___________________________________________________________________________
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


# FUNCTIONS and VIEWS
# ___________________________________________________________________________
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


# VIEW FOR ALGORITHMS VIEW
@app.route('/quantum_algorithms', methods=['GET'])
def index_quantum_algorithms_view():
    return render_template(
        template_name_or_list='index_algorithms.html'
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


@app.route('/quantum_algorithms/Bernstein_Vazirani_algorithm', methods=['GET', 'POST'])
def bernstein_vazirani_algorithm_view():
    if request.method == 'POST':
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '/static/files/berstein_vazirani_algorithm'
        if request.form['submit_button'] == 'Презентация':
            path = filepath + 'BVPresentation.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Упражнения':
            path = filepath + 'BVExercises.pdf'
            webbrowser.open_new_tab(path)
        elif request.form['submit_button'] == 'Вычислять':
            return redirect(
                url_for('bernstein_vazirani_algorithm')
            )
    return render_template(
        template_name_or_list='bernsteinvazirani_algorithm.html'
    )


@app.route('/quantum_algorithms/Grover_algorithm', methods=['GET', 'POST'])
def grover_algorithm_view():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Classical solution':
            return redirect(
                url_for('grover_classical_algorithm')
            )
        elif request.form['submit_button'] == 'Quantum solution':
            return redirect(
                url_for('grover_algorithm')
            )
        elif request.form['submit_button'] == 'Sudoku Quantum solution':
            return redirect(
                url_for('grover_sudoku_algorithm')
            )
    return render_template(
        template_name_or_list='grover_algorithm.html'
    )


@app.route('/quantum_algorithms/Quantum_Teleportation_algorithm', methods=['GET', 'POST'])
def quantum_teleportation_algorithm_view():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Вычислять':
            return redirect(
                url_for('quantum_teleportation_algorithm')
            )
    return render_template(
        template_name_or_list="quantumteleportation_algorithm.html"
    )


@app.route('/algorithms/Shor_algorithm', methods=['GET', 'POST'])
def shor_algorithm_view():
    if request.method == 'POST':
        if request.form['submit_button'] == 'QFT':
            return redirect(
                url_for('shor_algorithm_QFT')
            )
        elif request.form['submit_button'] == 'Circuit - QFT':
            return redirect(
                url_for('shor_algorithm_quantum_circuit_QFT')
            )
    return render_template(
        template_name_or_list="shor_algorithm.html"
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
@app.route('/quantum_algorithms/Bernstein_Vazirani_algorithm/quantum_solution', methods=['GET', 'POST'])
def bernstein_vazirani_algorithm():
    
    # DATA
    # INPUTS
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
@app.route('/quantum_algorithms/Grover_algorithm/quantum_solution', methods=['GET', 'POST'])
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


@app.route('/quantum_algorithms/Grover_algorithm/sudoku_solution', methods=['GET'])
def grover_sudoku_algorithm():
    clause_list = [ [0,1],
               [0,2],
               [1,3],
               [2,3] ]
    in_qubits = QuantumRegister(2, name='input')
    out_qubit = QuantumRegister(1, name='output')
    circuit = QuantumCircuit(in_qubits, out_qubit)
    XOR(circuit, in_qubits[0], in_qubits[1], out_qubit)
    draw_sudoku_example(
        circuit=circuit,
        filename="sudoku_circuit"
    )

    # Create separate registers to name bits
    var_qubits = QuantumRegister(4, name='v')  # variable bits
    clause_qubits = QuantumRegister(4, name='c')  # bits to store clause-checks
    circuit_dos = QuantumCircuit(var_qubits, clause_qubits)
    i = 0
    for clause in clause_list:
        XOR(circuit_dos, clause[0], clause[1], clause_qubits[i])
        i += 1
    draw_sudoku_example(
        circuit=circuit_dos,
        filename="sudoku_circuit"
    )

    # Create separate registers to name bits
    var_qubits = QuantumRegister(4, name='v')
    clause_qubits = QuantumRegister(4, name='c')
    output_qubit = QuantumRegister(1, name='out')
    circuit_tres = QuantumCircuit(var_qubits, clause_qubits, output_qubit)
    # Compute clauses
    i = 0
    for clause in clause_list:
        XOR(circuit_tres, clause[0], clause[1], clause_qubits[i])
        i += 1
    # Flip 'output' bit if all clauses are satisfied
    # MCT - Multiple Control X Gate
    circuit_tres.mct(clause_qubits, output_qubit)
    draw_sudoku_example(
        circuit=circuit_tres,
        filename="sudoku_circuit"
    )

    # REPETING STATES WITHOUT COMPUTING
    var_qubits = QuantumRegister(4, name='v')
    clause_qubits = QuantumRegister(4, name='c')
    output_qubit = QuantumRegister(1, name='out')
    cbits = ClassicalRegister(4, name='cbits')
    circuit_cuatro = QuantumCircuit(var_qubits, clause_qubits, output_qubit, cbits)
    sudoku_oracle(
        qc=circuit_cuatro,
        clause_list=clause_list,
        clause_qubits=clause_qubits,
        output_qubit=output_qubit
    )
    draw_sudoku_example(
        circuit=circuit_cuatro,
        filename="sudoku_circuit"
    )

    # FINAL ALGORITHM
    var_qubits = QuantumRegister(4, name='v')
    clause_qubits = QuantumRegister(4, name='c')
    output_qubit = QuantumRegister(1, name='out')
    cbits = ClassicalRegister(4, name='cbits')
    circuit_cinco = QuantumCircuit(var_qubits, clause_qubits, output_qubit, cbits)

    # Initialize 'out0' in state |->
    circuit_cinco.initialize([1, -1]/np.sqrt(2), output_qubit)

    # Initialize qubits in state |s>
    circuit_cinco.h(var_qubits)
    circuit_cinco.barrier()  # for visual separation

    ## First Iteration
    # Apply our oracle
    sudoku_oracle(circuit_cinco, clause_list, clause_qubits, output_qubit)
    circuit_cinco.barrier()  # for visual separation
    # Apply our diffuser
    circuit_cinco.append(diffuser(4), [0,1,2,3])

    ## Second Iteration
    sudoku_oracle(circuit_cinco, clause_list, clause_qubits, output_qubit)
    circuit_cinco.barrier()  # for visual separation
    # Apply our diffuser
    circuit_cinco.append(diffuser(4), [0,1,2,3])

    # Measure the variable qubits
    circuit_cinco.measure(var_qubits, cbits)

    circuit_cinco.draw(fold=-1)
    
    draw_sudoku_example(
        circuit=circuit_cinco,
        filename="sudoku_circuit"
    )

    # Simulate and plot results
    qasm_simulator = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(circuit_cinco, qasm_simulator)
    result = qasm_simulator.run(transpiled_qc).result()
    counts = result.get_counts()
    create_sudoku_histogram(
        counts=counts,
        name="sudoku_histogram"
    )

    return render_template(
        template_name_or_list="grover_algorithm.html"
    )

def XOR(qc, a, b, output):
    qc.cx(a, output)
    qc.cx(b, output)


def sudoku_oracle(qc, clause_list, clause_qubits, output_qubit):
    # Compute clauses
    i = 0
    for clause in clause_list:
        XOR(qc, clause[0], clause[1], clause_qubits[i])
        i += 1

    # Flip 'output' bit if all clauses are satisfied
    qc.mct(clause_qubits, output_qubit)

    # Uncompute clauses to reset clause-checking bits to 0
    i = 0
    for clause in clause_list:
        XOR(qc, clause[0], clause[1], clause_qubits[i])
        i += 1

def diffuser(nqubits):
    circuit = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range(nqubits):
        circuit.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range(nqubits):
        circuit.x(qubit)
    # Do multi-controlled-Z gate
    circuit.h(nqubits-1)
    circuit.mct(list(range(nqubits-1)), nqubits-1)  # multi-controlled-toffoli
    circuit.h(nqubits-1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range(nqubits):
        circuit.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range(nqubits):
        circuit.h(qubit)
    # We will return the diffuser as a gate
    U_s = circuit.to_gate()
    U_s.name = "U$_s$"
    return U_s


@app.route('/quantum_algorithms/Grover_algorithm/classical_solution', methods=['GET'])
def grover_classical_algorithm():
    # 7 is the last and 9 in the middle.
    element_tofind = 9
    my_list = [1,3,5,2,4,1,5,8,0,2,6,3,2,8,5,3,9,2,6,8,1,1,2,5,3,6,2,8,1,1,2,3,2,4,5,3,2,2,8,1,7,5]
    print(f'Number of elements: {len(my_list)}')
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
    
    # DATA
    # INPUTS
    num_qubits = 3
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


# Shor algorithm (QFT)
@app.route('/algorithms/Shor_Algorithm/QFT/quantum_solution', methods=['GET', 'POST'])
def shor_algorithm_QFT():

    state = '00'
    
    circuit = QuantumCircuit(len(state))
    circuit.initialize(
        Statevector.from_label(state).data,
        circuit.qubits[::-1]
    )
    print(f'Computational bases |{state}>')
    display(
        plot_bloch_multivector(Statevector.from_instruction(circuit).data)
    )
    plot.savefig(
        f'results/quantum_circuits/QFT_computational_bases_{NOW_TIME}.png'
    )
    print(f'Fourier bases |{state}>')
    circuit.append(
        QFT(len(state), do_swaps=True),
        circuit.qubits
    )
    display(
        plot_bloch_multivector(Statevector.from_instruction(circuit).data)
    )
    plot.savefig(
        f'results/quantum_circuits/QFT_fourier_bases_{NOW_TIME}.png'
    )
    return render_template(
        template_name_or_list="shor_algorithm.html"
    )


# Shor algorithm (QFT)
@app.route('/algorithms/Shor_Algorithm/Circuit_QFT/quantum_solution', methods=['GET', 'POST'])
def shor_algorithm_quantum_circuit_QFT():
    # Get value of PI
    num_qubits=4
    display(
        QFT(num_qubits).draw()
    )
    plot.savefig(
        f'results/quantum_circuits/Quantum_circuit_QFT_{NOW_TIME}.png'
    )
    return render_template(
        template_name_or_list="shor_algorithm.html"
    )

# No reconoce la libreria cu1
def my_qc_QFT(num_qubits):
    pi = np.pi
    circuit = QuantumCircuit(num_qubits)
    for qubit in range(num_qubits):
        circuit.h(qubit)
        for otherqubit in range(qubit+1, num_qubits):
            # https://qiskit.org/documentation/stable/0.24/stubs/qiskit.circuit.library.CU1Gate.html#qiskit.circuit.library.CU1Gate
            circuit.cu1(
                pi / (2**(otherqubit-qubit)), otherqubit, qubit
            )
    return circuit


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

