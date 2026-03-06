"""Lamport clocks algorithm — core logic, no UI."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EventType(Enum):
    INTERNAL = "internal"
    SEND = "send"
    RECEIVE = "receive"


@dataclass
class Event:
    """A single event in the distributed system."""
    process_id: int
    event_type: EventType
    timestamp: int  # Lamport timestamp
    label: str = ""
    # For SEND/RECEIVE: links to the paired event
    partner_process: Optional[int] = None
    partner_event_idx: Optional[int] = None


@dataclass
class Process:
    """A process with a Lamport clock."""
    id: int
    name: str
    clock: int = 0
    events: list[Event] = field(default_factory=list)
    crashed: bool = False

    def internal_event(self, label: str = "") -> Event:
        """Process an internal event."""
        self.clock += 1
        evt = Event(
            process_id=self.id,
            event_type=EventType.INTERNAL,
            timestamp=self.clock,
            label=label or f"e{len(self.events)}",
        )
        self.events.append(evt)
        return evt

    def send_event(self, label: str = "") -> Event:
        """Create a send event (message departs)."""
        self.clock += 1
        evt = Event(
            process_id=self.id,
            event_type=EventType.SEND,
            timestamp=self.clock,
            label=label or f"send",
        )
        self.events.append(evt)
        return evt

    def receive_event(self, sender_timestamp: int, sender_process: int,
                      sender_event_idx: int, label: str = "") -> Event:
        """Receive a message: clock = max(local, sender) + 1."""
        self.clock = max(self.clock, sender_timestamp) + 1
        evt = Event(
            process_id=self.id,
            event_type=EventType.RECEIVE,
            timestamp=self.clock,
            label=label or f"recv",
            partner_process=sender_process,
            partner_event_idx=sender_event_idx,
        )
        self.events.append(evt)
        return evt


@dataclass
class Message:
    """A message in transit between two processes."""
    sender: int
    receiver: int
    send_event_idx: int
    recv_event_idx: Optional[int] = None
    delivered: bool = False


@dataclass
class LamportSimulation:
    """Complete Lamport clock simulation state."""
    processes: list[Process] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    pending_steps: list[dict] = field(default_factory=list)
    step_index: int = 0

    def add_process(self, name: str) -> Process:
        p = Process(id=len(self.processes), name=name)
        self.processes.append(p)
        return p

    def plan_internal(self, process_id: int, label: str = ""):
        """Plan an internal event."""
        self.pending_steps.append({
            "type": "internal",
            "process": process_id,
            "label": label,
        })

    def plan_send(self, sender_id: int, receiver_id: int, label: str = ""):
        """Plan a send+receive pair."""
        self.pending_steps.append({
            "type": "message",
            "sender": sender_id,
            "receiver": receiver_id,
            "label": label,
        })

    def step(self) -> Optional[dict]:
        """Execute the next planned step. Returns the step or None if done."""
        if self.step_index >= len(self.pending_steps):
            return None

        action = self.pending_steps[self.step_index]
        self.step_index += 1

        if action["type"] == "internal":
            p = self.processes[action["process"]]
            if p.crashed:
                return {**action, "skipped": True, "reason": "crashed"}
            p.internal_event(action.get("label", ""))
            return action

        elif action["type"] == "message":
            sender = self.processes[action["sender"]]
            receiver = self.processes[action["receiver"]]

            if sender.crashed:
                return {**action, "skipped": True, "reason": "sender crashed"}

            send_evt = sender.send_event(action.get("label", ""))
            send_idx = len(sender.events) - 1

            # Link send event to receiver
            send_evt.partner_process = receiver.id

            if receiver.crashed:
                # Message lost
                msg = Message(
                    sender=sender.id,
                    receiver=receiver.id,
                    send_event_idx=send_idx,
                    delivered=False,
                )
                self.messages.append(msg)
                return {**action, "delivered": False, "reason": "receiver crashed"}

            recv_evt = receiver.receive_event(
                sender_timestamp=send_evt.timestamp,
                sender_process=sender.id,
                sender_event_idx=send_idx,
                label=action.get("label", ""),
            )
            recv_idx = len(receiver.events) - 1
            send_evt.partner_event_idx = recv_idx
            recv_evt.partner_event_idx = send_idx

            msg = Message(
                sender=sender.id,
                receiver=receiver.id,
                send_event_idx=send_idx,
                recv_event_idx=recv_idx,
                delivered=True,
            )
            self.messages.append(msg)
            return {**action, "delivered": True}

        return None

    def crash_process(self, process_id: int):
        """Crash a process — it stops responding."""
        self.processes[process_id].crashed = True

    def recover_process(self, process_id: int):
        """Recover a crashed process."""
        self.processes[process_id].crashed = False

    def get_state(self) -> dict:
        """Return full state for visualization."""
        return {
            "processes": [
                {
                    "id": p.id,
                    "name": p.name,
                    "clock": p.clock,
                    "crashed": p.crashed,
                    "events": [
                        {
                            "type": e.event_type.value,
                            "timestamp": e.timestamp,
                            "label": e.label,
                            "partner_process": e.partner_process,
                            "partner_event_idx": e.partner_event_idx,
                        }
                        for e in p.events
                    ],
                }
                for p in self.processes
            ],
            "messages": [
                {
                    "sender": m.sender,
                    "receiver": m.receiver,
                    "send_event_idx": m.send_event_idx,
                    "recv_event_idx": m.recv_event_idx,
                    "delivered": m.delivered,
                }
                for m in self.messages
            ],
            "step_index": self.step_index,
            "total_steps": len(self.pending_steps),
            "done": self.step_index >= len(self.pending_steps),
        }


def create_demo_scenario() -> LamportSimulation:
    """Create a simple 3-process demo scenario."""
    sim = LamportSimulation()
    sim.add_process("P0")
    sim.add_process("P1")
    sim.add_process("P2")

    # A sequence that shows the key Lamport clock behaviors:
    # 1. Internal events increment the clock
    # 2. Send/receive synchronize clocks
    # 3. The "max + 1" rule is visible
    sim.plan_internal(0, "compute")
    sim.plan_send(0, 1, "req")
    sim.plan_internal(2, "compute")
    sim.plan_send(1, 2, "fwd")
    sim.plan_internal(0, "compute")
    sim.plan_send(2, 0, "reply")
    sim.plan_send(0, 2, "ack")

    return sim
