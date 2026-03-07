"""
Jinja2 prompt template loader.
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Jinja2 environment
_env = Environment(
    loader=FileSystemLoader(PROMPTS_DIR),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(template_name: str, **kwargs) -> str:
    """
    Render a prompt template with the given variables.
    
    Args:
        template_name: Name of template file (e.g., "aggregate.jinja2")
        **kwargs: Variables to pass to the template
        
    Returns:
        Rendered prompt string
    """
    template = _env.get_template(template_name)
    return template.render(**kwargs)


# System prompt directory — plain text files, no Jinja rendering needed
_SYSTEM_PROMPT_DIR = PROMPTS_DIR / "system"


def load_system_prompt(name: str = "model-prompt") -> str:
    """
    Load a system prompt from the system/ subdirectory.

    Args:
        name: Filename stem (without .txt extension). Defaults to "default".

    Returns:
        The prompt text, stripped of leading/trailing whitespace.
    """
    path = _SYSTEM_PROMPT_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8").strip()

