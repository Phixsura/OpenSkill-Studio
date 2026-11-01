import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGpuPanel } from "@/components/fleet-gpu-panel";
describe("FleetGpuPanel", () => { it("renders", () => {
    const { container } = render(<FleetGpuPanel total={8} active={6} idle={2} avgUtil={55} wasteful={false} />);
    expect(container.textContent).toContain("GPU Fleet");
    expect(container.textContent).toContain("6 active");
}); });
