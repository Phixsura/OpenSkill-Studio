import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRespAiPanel } from "@/components/fleet-ai-resp-ai-panel";
describe("FleetAiRespAiPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRespAiPanel frameworks={3} active={3} assessments={1000} principles={30} compliance={99} />);
    expect(container.textContent).toContain("Responsible AI");
}); });
