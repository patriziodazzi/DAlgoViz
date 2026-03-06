"""CLI entry point for DAlgoViz."""

import webbrowser
from dalgoviz.server import create_app


def main():
    app = create_app()
    print("DAlgoViz v0.1.0 — http://localhost:5000")
    webbrowser.open("http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
