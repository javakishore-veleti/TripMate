from middleware.adapters.agentic.langgraph.llm_text import complete_text

_ROLE_TOKENS = {
    "classify": 350,
    "reason": 1100,
    "deep": 800,
}


def complete_role(role: str, system_prompt: str, user_prompt: str, state: dict) -> str:
    return complete_text(
        system_prompt,
        user_prompt,
        state,
        max_tokens=_ROLE_TOKENS.get(role, 700),
        job=role,
    )
