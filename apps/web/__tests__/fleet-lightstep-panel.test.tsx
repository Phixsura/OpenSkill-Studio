import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLightstepPanel } from "@/components/fleet-lightstep-panel";
describe("FleetLightstepPanel", () => { it("renders", () => {
    const { container } = render(<FleetLightstepPanel total={30} instrumented={25} latencyRegressions={2} coveragePct={83.3} />);
    expect(container.textContent).toContain("Lightstep");
    expect(container.textContent).toContain("2 latency");
}); });
