import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLivenessPanel } from "@/components/fleet-liveness-panel";
describe("FleetLivenessPanel", () => { it("renders", () => {
    const { container } = render(<FleetLivenessPanel total={20} failingPods={1} totalFailures={3} healthy={false} />);
    expect(container.textContent).toContain("Liveness Probes");
    expect(container.textContent).toContain("1 pods failing");
}); });
