import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOrchPanel } from "@/components/fleet-ai-orch-panel";
describe("FleetAiOrchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiOrchPanel />);
    expect(container.textContent).toContain("300,000+");
    expect(container.textContent).toContain("ALL SYSTEMS OPERATIONAL");
}); });
