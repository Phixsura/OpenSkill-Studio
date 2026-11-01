import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPostmortemPanel } from "@/components/fleet-ai-postmortem-panel";
describe("FleetAiPostmortemPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPostmortemPanel systems={2} active={2} postmortems={100} actionItems={400} completed={360} rate={90} />);
    expect(container.textContent).toContain("Postmortem");
}); });
