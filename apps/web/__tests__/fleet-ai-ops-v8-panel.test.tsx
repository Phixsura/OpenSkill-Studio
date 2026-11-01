import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOpsV8Panel } from "@/components/fleet-ai-ops-v8-panel";
describe("FleetAiOpsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiOpsV8Panel systems={5} active={5} automations={10000} autoResolved={50000} toil={99} />);
    expect(container.textContent).toContain("AI Ops v8");
}); });
