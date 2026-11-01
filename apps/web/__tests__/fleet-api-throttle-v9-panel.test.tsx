import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiThrottleV9Panel } from "@/components/fleet-api-throttle-v9-panel";
describe("FleetApiThrottleV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiThrottleV9Panel consumers={200} throttled={2} />);
    expect(container.textContent).toContain("API Throttle v9");
}); });
