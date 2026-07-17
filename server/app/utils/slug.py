import re
import unicodedata


def generate_slug(value: str) -> str:
    normalized_value = unicodedata.normalize(
        "NFKD",
        value.strip().lower(),
    )

    ascii_value = normalized_value.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        ascii_value,
    ).strip("-")

    return slug
