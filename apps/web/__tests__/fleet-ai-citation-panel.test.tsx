import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCitationPanel } from "@/components/fleet-ai-citation-panel";
describe("FleetAiCitationPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCitationPanel trackers={3} active={3} citations={20000000} verified={19500000} accuracy={97.5} />);
    expect(container.textContent).toContain("Citation Tracker");
}); });
