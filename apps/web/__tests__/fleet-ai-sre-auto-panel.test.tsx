import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSreAutoPanel } from "@/components/fleet-ai-sre-auto-panel";
describe("FleetAiSreAutoPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSreAutoPanel systems={4} active={4} toilReduced={80} automations={200} hoursSaved={10000} />);
    expect(container.textContent).toContain("SRE Automation");
}); });
