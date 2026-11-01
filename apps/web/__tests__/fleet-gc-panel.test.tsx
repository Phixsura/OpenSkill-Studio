import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGcPanel } from "@/components/fleet-gc-panel";
describe("FleetGcPanel", () => { it("renders", () => {
    const { container } = render(<FleetGcPanel avgPause={300} highPressure={true} />);
    expect(container.textContent).toContain("Fleet GC Pressure");
    expect(container.textContent).toContain("High GC pressure");
}); });
