import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOpsAutoV2Panel } from "@/components/fleet-ai-ops-auto-v2-panel";
describe("FleetAiOpsAutoV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiOpsAutoV2Panel systems={4} active={4} automations={1000} tasks={500000} manual={3} />);
    expect(container.textContent).toContain("Ops Automation v2");
}); });
