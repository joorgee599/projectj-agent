from dataclasses import dataclass, field
from typing import List, Callable


@dataclass
class AgentProfile:
    """Definition of an agent profile with its tools and prompt template."""

    name: str
    system_prompt_template: str
    tools: List[Callable] = field(default_factory=list)

    def build_prompt(self, **kwargs) -> str:
        """Render the system prompt with the given variables."""
        return self.system_prompt_template.format(**kwargs)
