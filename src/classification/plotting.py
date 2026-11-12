from pathlib import Path


def save_figure(fig, filename):
    folder = Path(__file__).resolve().parents[2] / "reports" / "figures"
    folder.mkdir(parents=True, exist_ok=True)

    name = Path(filename).name
    if not Path(name).suffix:
        name += ".png"
    path = folder / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print("file saved in: ", path)
    return path
