from qiskit.tools.visualization import plot_histogram


def create_histogram(counts, name):
    plot_histogram(
        counts,
        filename=f"results/histograms/{name}.png"
    )
