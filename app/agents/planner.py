"""
planner.py

The Planner Agent is the first node in our graph.
It asks the LLM which agents (tasks) need to run to build the trip plan,
and saves that list into state["plan"].
"""

from app.llm import get_llm, invoke_structured
from app.schemas.agent_schemas import PlannerOutput
from app.prompts.prompts import PLANNER_PROMPT
from app.state import TravelState


# Agents that actually exist as nodes in the graph. Anything the LLM
# returns outside this set would make route_decision() send LangGraph
# to a node that doesn't exist, causing a hard crash - so we filter
# the plan against this whitelist before saving it.
VALID_AGENTS = {
    "transport",
    "hotel",
    "weather",
    "places",
    "budget",
    "itinerary",
}


def planner_node(state: TravelState) -> TravelState:
    """
    Ask the LLM to decide which agents should run for this trip,
    using structured output so we get a clean Python list back.
    """
    llm = get_llm()

    structured_llm = llm.with_structured_output(PlannerOutput)

    prompt = PLANNER_PROMPT.format(
        source=state["source"],
        destination=state["destination"],
        days=state["days"],
        budget=state["budget"],
        user_request=state["user_request"],
    )

    result: PlannerOutput = invoke_structured(structured_llm, prompt)

    # ---------------------------------------------
    # Validate + normalize the plan
    # ---------------------------------------------

    raw_tasks = result.tasks or []

    plan = [
        task.strip().lower()
        for task in raw_tasks
        if task.strip().lower() in VALID_AGENTS
    ]

    # If validation stripped everything out (e.g. the LLM returned
    # garbage), fall back to the full standard plan rather than
    # silently returning nothing.
    if not plan:
        plan = ["transport", "hotel", "weather", "places", "itinerary", "budget"]

    print("=" * 50)
    print("Planner Output")
    print(plan)
    print("=" * 50)

    state["plan"] = plan
    state["current_step"] = 0

    return state