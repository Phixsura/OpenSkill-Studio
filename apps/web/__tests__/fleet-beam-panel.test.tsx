import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBeamPanel } from "@/components/fleet-beam-panel";
describe("FleetBeamPanel", () => { it("renders", () => {
    const { container } = render(<FleetBeamPanel total={10} running={8} drained={1} failed={1} />);
    expect(container.textContent).toContain("Beam");
    expect(container.textContent).toContain("1 failed");
}); });
