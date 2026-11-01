import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOpsV5Panel } from "@/components/fleet-ai-ops-v5-panel";
describe("FleetAiOpsV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiOpsV5Panel systems={5} active={5} automations={2000} tasks={2000000} toil={95} />);
    expect(container.textContent).toContain("AI Ops v5");
}); });
