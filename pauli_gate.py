def add_x_gate(circuit, qubit):
    circuit.x(
        qubit
    )
    return circuit


def add_z_gate(circuit, quantum_register, vector_register):
    register_a=vector_register[0]
    register_b=vector_register[1]
    circuit.cz(
        quantum_register[register_a],
        quantum_register[register_b]
    )
    return circuit
