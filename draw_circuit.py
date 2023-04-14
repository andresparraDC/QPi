import matplotlib.pyplot as plot


def draw(circuit, filename):
    circuit.draw(
        output='mpl',
        interactive= True
    )
    plot.savefig(
        f'results/quantum_circuits/{filename}.png')
