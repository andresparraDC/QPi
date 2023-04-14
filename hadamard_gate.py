def add_hadamard_gate(circuit, quantum_register, vector_register):
    for register in vector_register:
        circuit.h(
            quantum_register[register]
        )
    return circuit