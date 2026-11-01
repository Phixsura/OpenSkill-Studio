"""CLI commands — generate CLI commands for developer quick-start."""


def generate_init_commands(*, app_name: str, slug: str, category: str, runtime: str = "python3.12") -> list[str]:
    sdk = "openskill-sdk" if "python" in runtime else "@openskill/sdk"
    install = f"pip install {sdk}" if "python" in runtime else f"npm install {sdk}"
    return [
        f"# Initialize {app_name}",
        f"mkdir {slug} && cd {slug}",
        install,
        f"# Create manifest.json for {category} app",
        f"echo '{{\"schema_version\": \"1.0\", \"app\": {{\"name\": \"{app_name}\", \"slug\": \"{slug}\", \"version\": \"1.0.0\", \"category\": \"{category}\"}}, \"permissions\": [\"read:cohorts\"]}}' > manifest.json",
    ]


def generate_deploy_commands(slug: str) -> list[str]:
    return [
        f"# Deploy {slug}",
        f"openskill deploy --app {slug}",
        f"openskill logs --app {slug} --follow",
    ]
