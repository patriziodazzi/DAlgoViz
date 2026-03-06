"""CLI entry point for DAlgoViz."""

from dalgoviz.server import create_app


def main():
    app = create_app()
    print("DAlgoViz v0.1.0 — http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)


if __name__ == "__main__":
    main()
