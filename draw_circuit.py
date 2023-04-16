import matplotlib.pyplot as plot


def draw(circuit, filename):
    circuit.draw(
        # mpl - > images with color rendered purely in Python using matplotlib.
        output='mpl',
        interactive= True
    )
    plot.savefig(
        f'results/quantum_circuits/{filename}.png'
    )

def draw_sudoku_example(circuit, filename):
    circuit.draw(
        # mpl - > images with color rendered purely in Python using matplotlib.
        output='mpl',
        interactive= True
    )
    plot.savefig(
        f'results/examples/grover_algorithm/quantum_circuits/{filename}.png'
    )