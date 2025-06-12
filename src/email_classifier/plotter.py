import matplotlib.pyplot as plt
import os

def plot_category_distribution(category_counts, save_path: str = None):
    labels = list(category_counts.keys())
    sizes = list(category_counts.values())
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title("Distribution of Emails Across Categories")
    ax.axis('equal')
    if not os.environ.get('DISPLAY') and save_path:
        fig.savefig(save_path)
        print(f"Plot saved to {save_path}")
    return fig 