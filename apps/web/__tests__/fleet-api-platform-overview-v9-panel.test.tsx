import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPlatformOverviewV9Panel } from "@/components/fleet-api-platform-overview-v9-panel";
describe("FleetApiPlatformOverviewV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPlatformOverviewV9Panel />);
    expect(container.textContent).toContain("PLATFORM OVERVIEW");
    expect(container.textContent).toContain("A+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
