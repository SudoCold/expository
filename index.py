from pathlib import Path

from flask import Flask, abort, render_template, send_from_directory

ROOT = Path(__file__).resolve().parent
PAPERS_DIR = ROOT / "static" / "papers"
app = Flask(
    __name__,
    static_folder=str(ROOT / "static"),
    template_folder=str(ROOT / "templates"),
)

AUTHOR = "Manuel David P. Delos Santos"
DEPARTMENT = "Department of Electronics Engineering"
INSTITUTION = "FEU Institute of Technology"


TITLE_OVERRIDES = {
    "biscuit-conjecture": "The Biscuit Piece Pairing Problem",
    "clusss": "Cluster Theory",
}


def title_from_filename(name):
    stem = Path(name).stem
    if stem.lower() in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[stem.lower()]
    return stem.replace("-", " ").replace("_", " ").title()


def load_papers():
    if not PAPERS_DIR.exists():
        return []
    papers = []
    for path in sorted(PAPERS_DIR.glob("*.pdf"), key=lambda p: p.stem.lower()):
        papers.append(
            {
                "slug": path.stem.lower(),
                "title": title_from_filename(path.name),
                "filename": path.name,
                "pages": None,
                "category": "Expository",
                "summary": "An original expository paper from this archive.",
            }
        )
    return papers


def get_paper(slug):
    for paper in load_papers():
        if paper["slug"] == slug:
            return paper
    return None


@app.context_processor
def inject_globals():
    papers = load_papers()
    categories = sorted({paper["category"] for paper in papers})
    return {
        "author": AUTHOR,
        "department": DEPARTMENT,
        "institution": INSTITUTION,
        "paper_count": len(papers),
        "categories": categories,
    }


@app.route("/")
def home():
    return render_template("index.html", papers=load_papers())


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/paper/<slug>")
def paper_detail(slug):
    paper = get_paper(slug)
    if paper is None:
        abort(404)
    return render_template("paper.html", paper=paper)


@app.route("/download/<slug>")
def download_paper(slug):
    paper = get_paper(slug)
    if paper is None:
        abort(404)
    path = PAPERS_DIR / paper["filename"]
    if not path.exists():
        abort(404)
    return send_from_directory(PAPERS_DIR, paper["filename"], as_attachment=True)


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
