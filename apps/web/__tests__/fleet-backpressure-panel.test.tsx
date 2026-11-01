import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBackpressurePanel } from "@/components/fleet-backpressure-panel";
describe("FleetBackpressurePanel", () => { it("renders", () => {
    const { container } = render(<FleetBackpressurePanel total={10} pressured={2} dropped={500} stable={false} />);
    expect(container.textContent).toContain("Backpressure");
    expect(container.textContent).toContain("2 queues pressured");
}); });
