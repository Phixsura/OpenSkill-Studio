import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthPrbPanel } from "@/components/fleet-ai-health-prb-panel";
describe("FleetAiHealthPrbPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthPrbPanel probes={5} active={5} endpoints={500} checks={5000000} deps={100} allHealthy={true} />);
    expect(container.textContent).toContain("Health Probe v2");
}); });
