import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPlatformAnalyticsV9Panel } from "@/components/fleet-platform-analytics-v9-panel";
describe("FleetPlatformAnalyticsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPlatformAnalyticsV9Panel dau={10000} apiCalls={1000000} />);
    expect(container.textContent).toContain("Platform Analytics v9");
}); });
