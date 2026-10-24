import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCanaryAnlPanel } from "@/components/fleet-canary-anl-panel";
describe("FleetCanaryAnlPanel", () => { it("renders", () => {
    const { container } = render(<FleetCanaryAnlPanel errorDelta={0.5} latencyDelta={2} score={91} verdict="promote" />);
    expect(container.textContent).toContain("Canary Analysis");
    expect(container.textContent).toContain("PROMOTE");
}); });
