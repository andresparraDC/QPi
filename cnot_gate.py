def add_controlledX_gate(circuit, quantum_register, vector_register):
    register_a=vector_register[0]
    register_b=vector_register[1]
    circuit.cx(
        quantum_register[register_a],
        quantum_register[register_b]
    )
    return circuit