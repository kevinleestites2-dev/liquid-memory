import hashlib
import json
import os
import time
import random
from typing import Any, Optional

# ─────────────────────────────────────────────
# SECTION 1: STATES
# ─────────────────────────────────────────────

class State:
    CREATOR   = "CREATOR"
    ARCHITECT = "ARCHITECT"
    WARRIOR   = "WARRIOR"
    GHOST     = "GHOST"
    ORACLE    = "ORACLE"
    SAGE      = "SAGE"
    PHANTOM   = "PHANTOM"
    SOVEREIGN = "SOVEREIGN"

    ALL = [
        CREATOR, ARCHITECT, WARRIOR, GHOST,
        ORACLE, SAGE, PHANTOM, SOVEREIGN
    ]

    TRIGGERS = {
        CREATOR:   ["build", "create", "generate", "make", "design", "write", "code"],
        ARCHITECT: ["plan", "structure", "architect", "organize", "map", "blueprint"],
        WARRIOR:   ["defend", "block", "attack", "threat", "security", "audit", "protect", "rm", "format"],
        GHOST:     ["monitor", "watch", "observe", "silent", "track", "listen", "scan"],
        ORACLE:    ["analyze", "predict", "pattern", "forecast", "insight", "signal", "research"],
        SAGE:      ["learn", "reflect", "synthesize", "wisdom", "review", "lesson", "history"],
        PHANTOM:   ["edge", "lightweight", "minimal", "fast", "micro", "quick"],
        SOVEREIGN: ["command", "execute", "deploy", "launch", "orchestrate", "direct", "lead"],
    }

    LENSES = {
        CREATOR:   "Recall as raw material — fragments to be transformed into something new.",
        ARCHITECT: "Recall as structural blueprints — patterns, dependencies, and design decisions.",
        WARRIOR:   "Recall as threat intelligence — past vulnerabilities, blocked attacks, risk vectors.",
        GHOST:     "Recall as surveillance data — behavioral patterns, anomalies, silent observations.",
        ORACLE:    "Recall as predictive signal — trends, correlations, and future probabilities.",
        SAGE:      "Recall as accumulated wisdom — lessons learned, mistakes made, growth achieved.",
        PHANTOM:   "Recall as minimal footprint — only the most essential data, stripped bare.",
        SOVEREIGN: "Recall as executive intelligence — high-level decisions, outcomes, command history.",
    }


# ─────────────────────────────────────────────
# SECTION 2: DNA ENGINE
# ─────────────────────────────────────────────

class DNAEngine:
    @staticmethod
    def generate(agent_name: str, state: str, timestamp: float, previous_dna: str = "") -> str:
        raw = f"{agent_name}:{state}:{timestamp}:{previous_dna}:{random.getrandbits(64)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    @staticmethod
    def lineage(mutations: list) -> list:
        return [m.get("dna", "?") for m in mutations]


# ─────────────────────────────────────────────
# SECTION 3: MEMORY POOL
# ─────────────────────────────────────────────

class MemoryPool:
    def __init__(self, state: str):
        self.state = state
        self.lens = State.LENSES[state]
        self.events = []

    def absorb(self, event: dict):
        absorbed = {
            "original": event,
            "lens": self.lens,
            "state": self.state,
            "absorbed_at": time.time(),
            "interpretation": self._interpret(event),
        }
        self.events.append(absorbed)

    def _interpret(self, event: dict) -> str:
        task = event.get("task", "")
        result = str(event.get("result", ""))[:100]
        interpretations = {
            State.CREATOR:   f"Raw material available: '{task}' — can be transformed or rebuilt.",
            State.ARCHITECT: f"Structural record: '{task}' established pattern in system design.",
            State.WARRIOR:   f"Threat record: '{task}' — assess for risk vectors. Result: {result}",
            State.GHOST:     f"Observed: '{task}' at {event.get('timestamp', 0):.0f}. Silent log entry.",
            State.ORACLE:    f"Signal pattern: '{task}' correlates with outcome: {result}",
            State.SAGE:      f"Wisdom extracted: '{task}' taught — {result if result else 'lesson pending.'}",
            State.PHANTOM:   f"Minimal: {task[:30]}",
            State.SOVEREIGN: f"Command executed: '{task}'. Outcome: {result}. Filed for executive review.",
        }
        return interpretations.get(self.state, f"Event: {task}")

    def recall(self, n: int = 5) -> list:
        return self.events[-n:]

    def search(self, keyword: str) -> list:
        keyword = keyword.lower()
        return [
            e for e in self.events
            if keyword in str(e.get("original", {}).get("task", "")).lower()
            or keyword in str(e.get("interpretation", "")).lower()
        ]

    def to_dict(self) -> dict:
        return {"state": self.state, "events": self.events}

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryPool":
        pool = cls(data["state"])
        pool.events = data.get("events", [])
        return pool


# ─────────────────────────────────────────────
# SECTION 4: MUTATION ENGINE
# ─────────────────────────────────────────────

class MutationEngine:
    @staticmethod
    def detect_state(context: str, current_state: str) -> str:
        context_lower = context.lower()
        scores = {state: 0 for state in State.ALL}
        for state, keywords in State.TRIGGERS.items():
            for keyword in keywords:
                if keyword in context_lower:
                    scores[state] += 1
        best_state = max(scores, key=scores.get)
        if scores[best_state] == 0:
            return current_state
        return best_state

    @staticmethod
    def should_mutate(current: str, detected: str) -> bool:
        return current != detected


# ─────────────────────────────────────────────
# SECTION 5: LIQUID MEMORY
# ─────────────────────────────────────────────

class LiquidMemory:
    """
    Universal Liquid Memory for the Pantheon Ecosystem.

    from liquid_memory import LiquidMemory, PantheonBridge
    memory = PantheonBridge.for_any("Daedalus")
    memory.remember(task="build kairos tool", result="done")
    context = memory.context_summary()
    """

    def __init__(self, agent_name: str, initial_state: str = State.CREATOR,
                 storage_path: str = None, verbose: bool = True):
        self.agent_name = agent_name
        self.current_state = initial_state
        self.storage_path = storage_path or f"{agent_name.lower().replace('-','_')}_liquid_memory.json"
        self.verbose = verbose
        self.dna = DNAEngine.generate(agent_name, initial_state, time.time())
        self.mutations = []
        self.pools = {state: MemoryPool(state) for state in State.ALL}
        self.global_log = []
        self._load()
        if self.verbose:
            print(f"[LiquidMemory:{self.agent_name}] Initialized | State: {self.current_state} | DNA: {self.dna}")

    def remember(self, task: str, result: Any = None, metadata: dict = None):
        detected = MutationEngine.detect_state(task, self.current_state)
        if MutationEngine.should_mutate(self.current_state, detected):
            self.mutate(detected, trigger=task)

        event = {
            "task": task,
            "result": result,
            "state": self.current_state,
            "dna": self.dna,
            "timestamp": time.time(),
            "metadata": metadata or {},
        }
        for pool in self.pools.values():
            pool.absorb(event)
        self.global_log.append(event)
        self._save()
        if self.verbose:
            print(f"[LiquidMemory:{self.agent_name}] Remembered | State: {self.current_state} | Task: {task[:50]}")

    def recall(self, n: int = 5, state: str = None) -> list:
        target_state = state or self.current_state
        pool = self.pools.get(target_state)
        if not pool:
            return []
        return pool.recall(n)

    def recall_all_states(self, task_keyword: str) -> dict:
        results = {}
        for state, pool in self.pools.items():
            hits = pool.search(task_keyword)
            if hits:
                results[state] = hits[-1].get("interpretation", "")
        return results

    def search(self, keyword: str, state: str = None) -> list:
        target_state = state or self.current_state
        return self.pools[target_state].search(keyword)

    def context_summary(self, n: int = 3) -> str:
        recent = self.recall(n)
        if not recent:
            return f"[{self.agent_name}] No prior memory. State: {self.current_state}. DNA: {self.dna}"
        lines = [
            f"[LiquidMemory] Agent: {self.agent_name} | State: {self.current_state} | DNA: {self.dna}",
            f"Lens: {State.LENSES[self.current_state]}",
            "Recent memory:",
        ]
        for m in recent:
            lines.append(f"  — {m.get('interpretation', m.get('original', {}).get('task', ''))}")
        return "\n".join(lines)

    def mutate(self, new_state: str, trigger: str = "", forced: bool = False):
        if new_state not in State.ALL:
            print(f"[LiquidMemory] Unknown state: {new_state}")
            return
        old_state = self.current_state
        old_dna = self.dna
        self.current_state = new_state
        self.dna = DNAEngine.generate(self.agent_name, new_state, time.time(), old_dna)
        mutation_record = {
            "from": old_state,
            "to": new_state,
            "trigger": trigger[:100] if trigger else "manual",
            "forced": forced,
            "old_dna": old_dna,
            "dna": self.dna,
            "timestamp": time.time(),
        }
        self.mutations.append(mutation_record)
        self._save()
        if self.verbose:
            print(f"[LiquidMemory:{self.agent_name}] MUTATED {old_state} → {new_state} | DNA: {self.dna}")

    def force_state(self, state: str):
        self.mutate(state, trigger="forced", forced=True)

    def lineage(self) -> list:
        return DNAEngine.lineage(self.mutations)

    def mutation_history(self) -> list:
        return self.mutations

    def state_distribution(self) -> dict:
        return {state: len(pool.events) for state, pool in self.pools.items()}

    def status(self) -> dict:
        return {
            "agent": self.agent_name,
            "current_state": self.current_state,
            "dna": self.dna,
            "total_events": len(self.global_log),
            "total_mutations": len(self.mutations),
            "state_distribution": self.state_distribution(),
            "lineage": self.lineage()[-5:],
        }

    def _save(self):
        try:
            data = {
                "agent_name": self.agent_name,
                "current_state": self.current_state,
                "dna": self.dna,
                "mutations": self.mutations,
                "global_log": self.global_log[-500:],
                "pools": {state: pool.to_dict() for state, pool in self.pools.items()},
                "saved_at": time.time(),
            }
            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[LiquidMemory] Save error: {e}")

    def _load(self):
        if not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
            self.current_state = data.get("current_state", self.current_state)
            self.dna = data.get("dna", self.dna)
            self.mutations = data.get("mutations", [])
            self.global_log = data.get("global_log", [])
            for state, pool_data in data.get("pools", {}).items():
                if state in self.pools:
                    self.pools[state] = MemoryPool.from_dict(pool_data)
            if self.verbose:
                print(f"[LiquidMemory:{self.agent_name}] Loaded from {self.storage_path}")
        except Exception as e:
            print(f"[LiquidMemory] Load error: {e}")

    def wipe(self):
        self.pools = {state: MemoryPool(state) for state in State.ALL}
        self.mutations = []
        self.global_log = []
        self.dna = DNAEngine.generate(self.agent_name, self.current_state, time.time())
        self._save()
        print(f"[LiquidMemory:{self.agent_name}] WIPED. Fresh state: {self.current_state} | DNA: {self.dna}")


# ─────────────────────────────────────────────
# SECTION 6: PANTHEON BRIDGE
# ─────────────────────────────────────────────

class PantheonBridge:
    @staticmethod
    def for_kairos(agent_name: str, initial_state: str = State.CREATOR) -> LiquidMemory:
        return LiquidMemory(agent_name=agent_name, initial_state=initial_state,
                            storage_path=f"kairos_{agent_name.lower()}_liquid.json")

    @staticmethod
    def for_claw_prime(initial_state: str = State.SOVEREIGN) -> LiquidMemory:
        return LiquidMemory(agent_name="Claw-Prime", initial_state=initial_state,
                            storage_path="claw_prime_liquid.json")

    @staticmethod
    def for_zeus(initial_state: str = State.SOVEREIGN) -> LiquidMemory:
        return LiquidMemory(agent_name="Zeus-Prime", initial_state=initial_state,
                            storage_path="zeus_prime_liquid.json")

    @staticmethod
    def for_any(bot_name: str, initial_state: str = State.CREATOR) -> LiquidMemory:
        return LiquidMemory(agent_name=bot_name, initial_state=initial_state,
                            storage_path=f"{bot_name.lower().replace('-','_')}_liquid.json")


# ─────────────────────────────────────────────
# SECTION 7: DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  L I Q U I D   M E M O R Y  —  Pantheon Demo")
    print("="*60 + "\n")

    memory = PantheonBridge.for_claw_prime()

    tasks = [
        ("research Solana TVL signals", "High TVL growth detected"),
        ("build the new swarm executor module", "Module scaffolded"),
        ("audit rm -rf command detected in pipeline", "BLOCKED by IronGate"),
        ("monitor INTEL_BUS for anomalies", "3 signals observed"),
        ("analyze pattern in last 10 tasks", "Recurring research → build cycle detected"),
        ("learn from the blocked security event", "IronGate pattern logged as wisdom"),
        ("deploy Kairos Alpha crew", "Crew online, 3 agents active"),
        ("command all Legion pieces to sync state", "12/12 agents synchronized"),
    ]

    for task, result in tasks:
        memory.remember(task=task, result=result)
        print()

    print("\n" + "="*60)
    print("  MEMORY STATUS")
    print("="*60)
    for key, val in memory.status().items():
        print(f"  {key}: {val}")
