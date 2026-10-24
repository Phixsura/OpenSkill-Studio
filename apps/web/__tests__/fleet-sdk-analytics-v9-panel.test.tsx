import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSdkAnalyticsV9Panel } from "@/components/fleet-sdk-analytics-v9-panel";
describe("FleetSdkAnalyticsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSdkAnalyticsV9Panel sdks={5} downloads={50000} />);
    expect(container.textContent).toContain("SDK Analytics v9");
}); });
