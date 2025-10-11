from google.adk.agents import Agent
from .adk_security_tool import analyze_security

security_agent = Agent(
    name="security_guard_agent",
    model="gemini-2.5-flash",
    description=(
        "Agent that evaluates user instructions for security risks using a custom tool."
    ),
    instruction=(
        "You are a strict security guard. When the user provides an instruction, "
        "call the analyze_security tool with the exact text. Do not transform or paraphrase "
        "the input. Return ONLY the JSON from the tool without additional commentary."
    ),
    tools=[analyze_security],
)