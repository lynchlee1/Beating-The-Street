"""HTML injector — combines the pre-built React single-file template with
the parsed financial JSON data to produce an offline-ready static HTML file.
"""

import json
import os
from pathlib import Path


# Default location of the Vite single-file build output
_DEFAULT_TEMPLATE = Path(__file__).parent.parent / "ui" / "dist" / "index.html"


def generate_static_html(
    parsed_data: dict,
    output_path: str | Path = "report.html",
    template_path: str | Path | None = None,
) -> Path:
    """Inject *parsed_data* into the React template and write *output_path*.

    Parameters
    ----------
    parsed_data:
        The JSON-serialisable dict produced by ``src.parser.build_parsed_data``.
    output_path:
        Destination HTML file path.  Parent directories are created as needed.
    template_path:
        Path to the built React single-file HTML.  Defaults to
        ``src/ui/dist/index.html``.

    Returns
    -------
    Path
        Absolute path to the written file.
    """
    if template_path is None:
        template_path = _DEFAULT_TEMPLATE

    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(
            f"React build template not found at: {template_path}\n"
            "Run `npm run build` inside src/ui/ first."
        )

    html = template_path.read_text(encoding="utf-8")

    # Serialise the payload; use a compact encoder so the file stays small
    json_str = json.dumps(parsed_data, ensure_ascii=False, separators=(",", ":"))

    # Inject right before </head> so the global is available when the app mounts
    injection = f"<script>window.__INITIAL_DATA__ = {json_str};</script>"
    if "</head>" in html:
        html = html.replace("</head>", f"{injection}\n</head>", 1)
    else:
        # Fallback: prepend to body
        html = injection + "\n" + html

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    print(f"✅  Offline report written to: {output_path.resolve()}")
    return output_path.resolve()
