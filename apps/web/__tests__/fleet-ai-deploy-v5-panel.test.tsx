import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDeployV5Panel } from "@/components/fleet-ai-deploy-v5-panel";
describe("FleetAiDeployV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDeployV5Panel deployers={5} active={5} deploys={2000} rollbacks={0} leadMin={2} failPct={0.05} />);
    expect(container.textContent).toContain("AI Deploy v5");
}); });
