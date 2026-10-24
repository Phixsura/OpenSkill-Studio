import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetThrottlePanel } from "@/components/fleet-throttle-panel";
describe("FleetThrottlePanel", () => { it("renders", () => {
    const { container } = render(<FleetThrottlePanel total={10} throttled={2} heavy={1} clean={false} />);
    expect(container.textContent).toContain("API Throttling");
    expect(container.textContent).toContain("2 throttled");
}); });
