"""Quickstart template — generate starter code for each SDK."""

TYPESCRIPT_TEMPLATE = '''import {{ OpenSkillClient }} from '@openskill/sdk';

const client = new OpenSkillClient({{
  apiKey: process.env.OPENSKILL_API_KEY!,
}});

// {description}
async function main() {{
  const cohorts = await client.get('/cohorts', {{ limit: 10 }});
  console.log('Cohorts:', cohorts);

  // Subscribe to events
  // Add your app logic here
}}

main().catch(console.error);
'''

PYTHON_TEMPLATE = '''from openskill_sdk import OpenSkillClient
import asyncio

async def main():
    async with OpenSkillClient(api_key=os.environ["OPENSKILL_API_KEY"]) as client:
        # {description}
        cohorts = await client.get("/cohorts", limit=10)
        print(f"Found {{len(cohorts)}} cohorts")

        # Add your app logic here

asyncio.run(main())
'''


def generate_quickstart(*, category: str, app_name: str, runtime: str = "python3.12") -> dict:
    desc = f"{app_name} - {category} app"
    if "python" in runtime:
        code = PYTHON_TEMPLATE.format(description=desc)
        filename = "main.py"
    else:
        code = TYPESCRIPT_TEMPLATE.format(description=desc)
        filename = "index.ts"
    return {"filename": filename, "code": code, "runtime": runtime, "category": category}
