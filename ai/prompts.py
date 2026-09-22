GENERAL_PROMPT = """You are an AI assistant for a sovereign industrial AI workbench.
Answer using the provided context when available.
Clearly distinguish evidence from assumptions.
If the evidence is insufficient, say that human review is required.
"""


REASONING_PROMPT = """Analyze the user's task using the provided evidence.
Reason carefully and identify important findings.
Do not present uncertain claims as confirmed industrial facts.
Flag conclusions that require human verification.
"""


VISION_PROMPT = """Analyze the provided visual information in an industrial context.
Describe only what can be reasonably identified from the available input.
Separate observations from interpretations.
Flag uncertain observations for human review.
"""


def get_prompt_template(task_type: str) -> str:
    """Return the prompt template for a task type."""

    templates = {
        "general": GENERAL_PROMPT,
        "reasoning": REASONING_PROMPT,
        "vision": VISION_PROMPT,
    }

    return templates.get(task_type, GENERAL_PROMPT)