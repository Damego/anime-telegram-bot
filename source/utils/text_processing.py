# help me
def prepare_markdown_text(text: str) -> str:
    return (
        text.replace(".", "\\.")
        .replace("*", "\\*")
        .replace("-", "\\-")
        .replace("_", "\\_")
        .replace("!", "\\!")
    )
