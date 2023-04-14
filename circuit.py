from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


def create_circuit(num_qubits, num_bits):
    quantum_register = QuantumRegister(num_qubits)
    classical_register = ClassicalRegister(num_bits)
    circuit = QuantumCircuit(quantum_register, classical_register)
    return circuit, quantum_register
