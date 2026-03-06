"""Scalability laws — pure math, no simulation."""

import math
from dataclasses import dataclass


@dataclass
class AmdahlResult:
    """Result of Amdahl's law computation."""
    processors: list[int]
    speedup: list[float]
    serial_fraction: float


def amdahl(serial_fraction: float, max_processors: int = 64) -> AmdahlResult:
    """Amdahl's law: S(N) = 1 / (f + (1-f)/N).

    Args:
        serial_fraction: fraction of work that is serial (0..1)
        max_processors: compute up to this many processors
    """
    procs = list(range(1, max_processors + 1))
    speedup = [1.0 / (serial_fraction + (1 - serial_fraction) / n) for n in procs]
    return AmdahlResult(processors=procs, speedup=speedup, serial_fraction=serial_fraction)


@dataclass
class GustafsonResult:
    """Result of Gustafson's law computation."""
    processors: list[int]
    scaled_speedup: list[float]
    serial_fraction: float


def gustafson(serial_fraction: float, max_processors: int = 64) -> GustafsonResult:
    """Gustafson's law: S(N) = N - f*(N-1).

    Assumes problem size scales with processors (scaled speedup).

    Args:
        serial_fraction: fraction of work that is serial (0..1)
        max_processors: compute up to this many processors
    """
    procs = list(range(1, max_processors + 1))
    scaled = [n - serial_fraction * (n - 1) for n in procs]
    return GustafsonResult(processors=procs, scaled_speedup=scaled, serial_fraction=serial_fraction)


@dataclass
class USLResult:
    """Result of Universal Scalability Law computation."""
    processors: list[int]
    throughput: list[float]
    sigma: float
    kappa: float


def usl(sigma: float, kappa: float, max_processors: int = 64) -> USLResult:
    """Universal Scalability Law: C(N) = N / (1 + σ(N-1) + κN(N-1)).

    Args:
        sigma: contention coefficient (serial fraction, 0..1)
        kappa: coherency coefficient (crosstalk/cache invalidation, 0..1)
        max_processors: compute up to this many processors
    """
    procs = list(range(1, max_processors + 1))
    throughput = [
        n / (1 + sigma * (n - 1) + kappa * n * (n - 1))
        for n in procs
    ]
    return USLResult(processors=procs, throughput=throughput, sigma=sigma, kappa=kappa)


@dataclass
class LittleResult:
    """Result of Little's law computation."""
    arrival_rate: float  # λ (requests/sec)
    avg_time_in_system: float  # W (seconds)
    avg_items_in_system: float  # L = λW


def little(arrival_rate: float, avg_time_in_system: float) -> LittleResult:
    """Little's law: L = λW.

    Args:
        arrival_rate: average arrival rate (λ, requests/sec)
        avg_time_in_system: average time a request spends in system (W, seconds)
    """
    return LittleResult(
        arrival_rate=arrival_rate,
        avg_time_in_system=avg_time_in_system,
        avg_items_in_system=arrival_rate * avg_time_in_system,
    )
