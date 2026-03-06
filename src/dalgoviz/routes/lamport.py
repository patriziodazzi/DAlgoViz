"""Routes for Lamport clocks simulation."""

from flask import Blueprint, jsonify, request, session
from dalgoviz.algorithms.lamport import LamportSimulation, create_demo_scenario

lamport_bp = Blueprint("lamport", __name__, url_prefix="/api/lamport")

# In-memory simulation store (single-user tool, no DB needed)
_simulations: dict[str, LamportSimulation] = {}


def _get_or_create_sim(sim_id: str = "default") -> LamportSimulation:
    if sim_id not in _simulations:
        _simulations[sim_id] = create_demo_scenario()
    return _simulations[sim_id]


@lamport_bp.route("/state")
def get_state():
    sim_id = request.args.get("id", "default")
    sim = _get_or_create_sim(sim_id)
    return jsonify(sim.get_state())


@lamport_bp.route("/step", methods=["POST"])
def step():
    sim_id = request.json.get("id", "default") if request.json else "default"
    sim = _get_or_create_sim(sim_id)
    result = sim.step()
    return jsonify({
        "action": result,
        "state": sim.get_state(),
    })


@lamport_bp.route("/reset", methods=["POST"])
def reset():
    sim_id = request.json.get("id", "default") if request.json else "default"
    _simulations[sim_id] = create_demo_scenario()
    return jsonify(_simulations[sim_id].get_state())


@lamport_bp.route("/crash", methods=["POST"])
def crash():
    data = request.json or {}
    sim_id = data.get("id", "default")
    process_id = int(data.get("process_id", 0))
    sim = _get_or_create_sim(sim_id)
    sim.crash_process(process_id)
    return jsonify(sim.get_state())


@lamport_bp.route("/recover", methods=["POST"])
def recover():
    data = request.json or {}
    sim_id = data.get("id", "default")
    process_id = int(data.get("process_id", 0))
    sim = _get_or_create_sim(sim_id)
    sim.recover_process(process_id)
    return jsonify(sim.get_state())


@lamport_bp.route("/run-all", methods=["POST"])
def run_all():
    """Execute all remaining steps at once."""
    sim_id = request.json.get("id", "default") if request.json else "default"
    sim = _get_or_create_sim(sim_id)
    while sim.step() is not None:
        pass
    return jsonify(sim.get_state())
