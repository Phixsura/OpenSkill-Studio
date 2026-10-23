"""App quickstart guide — generate step-by-step getting started guides."""


def generate_quickstart(*, app_name: str, sdk: str, framework: str | None = None) -> dict:
    steps = [
        {"step": 1, "title": "Install the SDK", "code": _install_cmd(sdk, app_name),
         "language": "bash"},
        {"step": 2, "title": "Initialize the Client", "code": _init_code(sdk, app_name),
         "language": sdk},
        {"step": 3, "title": "Make Your First API Call", "code": _first_call(sdk),
         "language": sdk},
        {"step": 4, "title": "Handle the Response", "code": _handle_response(sdk),
         "language": sdk},
    ]
    return {
        "app_name": app_name,
        "sdk": sdk,
        "framework": framework,
        "steps": steps,
        "total_steps": len(steps),
        "estimated_time_min": 5,
    }


def _install_cmd(sdk: str, name: str) -> str:
    if sdk == "typescript":
        return f"npm install @openskill/{name.lower().replace(' ', '-')}"
    return f"pip install openskill-{name.lower().replace(' ', '-')}"


def _init_code(sdk: str, name: str) -> str:
    if sdk == "typescript":
        return f'import {{ {name.replace(" ", "")} }} from "@openskill/{name.lower().replace(" ", "-")}";\n\nconst client = new {name.replace(" ", "")}({{ apiKey: process.env.API_KEY }});'
    return f'from openskill.{name.lower().replace(" ", "_")} import Client\n\nclient = Client(api_key=os.environ["API_KEY"])'


def _first_call(sdk: str) -> str:
    if sdk == "typescript":
        return 'const result = await client.apps.list();\nconsole.log(result.data);'
    return 'result = client.apps.list()\nprint(result.data)'


def _handle_response(sdk: str) -> str:
    if sdk == "typescript":
        return 'if (result.data.length > 0) {\n  console.log("Found apps:", result.data.length);\n}'
    return 'if result.data:\n    print(f"Found {len(result.data)} apps")'
