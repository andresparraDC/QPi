from qiskit.tools.visualization import plot_histogram


def create_histogram(counts, name):
    legend = ['Execution']
    plot_histogram(
        counts,
        legend=legend,
        color=['crimson','midnightblue'],
        # x and y [inches]
        figsize = (25, 10),
        title=f" -- {name} -- ",
        filename=f"results/histograms/{name}.png"
    )

def create_sudoku_histogram(counts, name):
    legend = ['Execution']
    plot_histogram(
        counts,
        legend=legend,
        color=['crimson','midnightblue'],
        # x and y [inches]
        figsize = (25, 10),
        title=f" -- {name} -- ",
        filename=f"results/examples/grover_algorithm/histograms/{name}.png"
    )
