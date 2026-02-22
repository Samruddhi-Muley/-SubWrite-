import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.nl2br import Nl2BrExtension


def render_markdown(text):
    """
    Convert markdown text to HTML
    """
    if not text:
        return ""

    md = markdown.Markdown(
        extensions=[
            'fenced_code',  # Code blocks with ```
            'tables',  # Tables
            'nl2br',  # Convert newlines to <br>
            'codehilite',  # Syntax highlighting
            'extra',  # Extra features (footnotes, etc.)
        ]
    )

    return md.convert(text)