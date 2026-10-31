import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReleaseGateV9Panel } from "@/components/fleet-release-gate-v9-panel";
describe("FleetReleaseGateV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetReleaseGateV9Panel releases={100} blocked={0} />);
    expect(container.textContent).toContain("Release Gate v9");
}); });
