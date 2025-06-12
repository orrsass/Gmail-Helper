from email_classifier.plotter import plot_category_distribution
import tempfile
import os

def test_plot_category_distribution_returns_figure():
    data = {"A": 1, "B": 2}
    fig = plot_category_distribution(data)
    assert fig is not None
    assert hasattr(fig, 'savefig')

def test_plot_category_distribution_saves_file():
    data = {"A": 1, "B": 2}
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        path = tmp.name
    try:
        fig = plot_category_distribution(data, save_path=path)
        assert os.path.exists(path)
    finally:
        os.remove(path) 