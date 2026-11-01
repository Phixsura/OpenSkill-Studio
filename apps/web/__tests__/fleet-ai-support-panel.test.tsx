import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSupportPanel } from "@/components/fleet-ai-support-panel";
describe("FleetAiSupportPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSupportPanel systems={3} active={3} tickets={10000} autoResolved={8000} resolution={3} csat={4.8} />);
    expect(container.textContent).toContain("AI Support");
}); });
