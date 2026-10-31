import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSyntheticMonitorV9Panel } from "@/components/fleet-synthetic-monitor-v9-panel";
describe("FleetSyntheticMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSyntheticMonitorV9Panel checks={50} passing={50} />);
    expect(container.textContent).toContain("Synthetic Monitor v9");
}); });
