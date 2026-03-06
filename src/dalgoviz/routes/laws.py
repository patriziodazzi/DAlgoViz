"""Routes for scalability laws."""

from flask import Blueprint, jsonify, request

from dalgoviz.laws import amdahl, gustafson, usl, little

laws_bp = Blueprint("laws", __name__, url_prefix="/api/laws")


@laws_bp.route("/amdahl")
def api_amdahl():
    f = float(request.args.get("f", 0.1))
    n = int(request.args.get("n", 64))
    result = amdahl(f, n)
    return jsonify({
        "processors": result.processors,
        "speedup": result.speedup,
        "serial_fraction": result.serial_fraction,
        "theoretical_max": 1.0 / f if f > 0 else float("inf"),
    })


@laws_bp.route("/gustafson")
def api_gustafson():
    f = float(request.args.get("f", 0.1))
    n = int(request.args.get("n", 64))
    result = gustafson(f, n)
    return jsonify({
        "processors": result.processors,
        "scaled_speedup": result.scaled_speedup,
        "serial_fraction": result.serial_fraction,
    })


@laws_bp.route("/usl")
def api_usl():
    sigma = float(request.args.get("sigma", 0.05))
    kappa = float(request.args.get("kappa", 0.01))
    n = int(request.args.get("n", 64))
    result = usl(sigma, kappa, n)
    peak_idx = max(range(len(result.throughput)), key=lambda i: result.throughput[i])
    return jsonify({
        "processors": result.processors,
        "throughput": result.throughput,
        "sigma": result.sigma,
        "kappa": result.kappa,
        "peak_processors": result.processors[peak_idx],
        "peak_throughput": result.throughput[peak_idx],
    })


@laws_bp.route("/little")
def api_little():
    lam = float(request.args.get("lambda", 100))
    w = float(request.args.get("w", 0.05))
    result = little(lam, w)
    return jsonify({
        "arrival_rate": result.arrival_rate,
        "avg_time_in_system": result.avg_time_in_system,
        "avg_items_in_system": result.avg_items_in_system,
    })
