import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCpuThrottlePanel } from "@/components/fleet-cpu-throttle-panel";
describe("FleetCpuThrottlePanel", () => { it("renders", () => {
    const { container } = render(<FleetCpuThrottlePanel total={30} throttled={5} severe={2} healthy={false} />);
    expect(container.textContent).toContain("CPU Throttling");
    expect(container.textContent).toContain("2 severely");
}); });
