import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiThreatIntPanel } from "@/components/fleet-ai-threat-int-panel";
describe("FleetAiThreatIntPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiThreatIntPanel feeds={5} active={5} indicators={500000} threats={100} mitigated={100} />);
    expect(container.textContent).toContain("Threat Intelligence");
}); });
