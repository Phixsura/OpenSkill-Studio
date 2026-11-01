import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDragonflyPanel } from "@/components/fleet-dragonfly-panel";
describe("FleetDragonflyPanel", () => { it("renders", () => {
    const { container } = render(<FleetDragonflyPanel instances={3} running={3} memoryGb={192} opsPerSec={6000000} />);
    expect(container.textContent).toContain("Dragonfly");
    expect(container.textContent).toContain("6,000,000");
}); });
