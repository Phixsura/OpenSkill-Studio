import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiAvailabilityV9Panel } from "@/components/fleet-api-availability-v9-panel";
describe("FleetApiAvailabilityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiAvailabilityV9Panel regions={12} uptime={99.999} />);
    expect(container.textContent).toContain("API Availability v9");
}); });
