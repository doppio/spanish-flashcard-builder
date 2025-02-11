from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def load_template(path: str) -> str:
    """Load a template file from the templates directory."""
    return (TEMPLATES_DIR / path).read_text()


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render a template with the given context."""
    template = env.get_template(template_name)
    return template.render(**context)
