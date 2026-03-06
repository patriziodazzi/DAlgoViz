"""Flask application factory for DAlgoViz."""

from flask import Flask


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    from dalgoviz.routes.laws import laws_bp
    from dalgoviz.routes.lamport import lamport_bp

    app.register_blueprint(laws_bp)
    app.register_blueprint(lamport_bp)

    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    return app
