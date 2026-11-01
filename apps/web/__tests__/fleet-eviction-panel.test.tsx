import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEvictionPanel } from "@/components/fleet-eviction-panel";
describe("FleetEvictionPanel", () => { it("renders", () => {
    const { container } = render(<FleetEvictionPanel total={15} highRate={true} />);
    expect(container.textContent).toContain("Pod Evictions");
    expect(container.textContent).toContain("High eviction rate");
}); });
