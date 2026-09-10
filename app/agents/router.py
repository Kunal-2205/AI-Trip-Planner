"""
router.py

The Router is the "traffic controller" of our graph.
It looks at state["plan"] (the ordered list of agents to run) and
state["current_step"] (how far we've gotten), and decides which
agent should run next by setting state["next_agent"].

We reuse this SAME router node after every agent finishes, instead of
creating a separate router node for each step. This keeps the graph
simple while still matching the "Planner -> Router -> Agent -> Router
-> Agent -> ..." flow.
"""

from app.state import TravelState


# Must match the keys used in graph.py's add_conditional_edges mapping.
KNOWN_AGENTS = {
    "transport",
    "hotel",
    "weather",
    "places",
    "budget",
    "itinerary",
}


def router_node(state: TravelState) -> TravelState:
    """
    Look at the plan and current_step, and decide the next agent.
    """
    plan = state.get("plan", [])
    step = state.get("current_step", 0)

    if step < len(plan):
        candidate = plan[step]

        # Defensive check: planner_node already filters the plan
        # against a whitelist, but if state["plan"] is ever set some
        # other way (manual testing, future callers, etc.) an unknown
        # agent name here would make route_decision() point LangGraph
        # at a node that doesn't exist and crash the whole run.
        # Skip anything unrecognized instead of failing.
        if candidate in KNOWN_AGENTS:
            state["next_agent"] = candidate
        else:
            print(f"[WARNING] Unknown agent '{candidate}' in plan, skipping.")
            state["current_step"] += 1
            return router_node(state)
    else:
        # We've run every agent in the plan - we're done
        state["next_agent"] = "end"

    return state


def route_decision(state: TravelState) -> str:
    """
    LangGraph calls this function after the router node runs.
    It simply returns the value of next_agent, which LangGraph
    uses to pick the next node to visit.
    """
    return state["next_agent"]