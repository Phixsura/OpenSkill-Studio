import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetZigPanel } from "@/components/fleet-zig-panel";
describe("FleetZigPanel", () => { it("renders", () => {
    const { container } = render(<FleetZigPanel services={3} running={3} rps={1500000} avgMemory={400} />);
    expect(container.textContent).toContain("Zig");
    expect(container.textContent).toContain("1,500,000");
}); });
