import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiUsagePanel } from "@/components/fleet-api-usage-panel";
describe("FleetApiUsagePanel", () => { it("renders", () => {
    const { container } = render(<FleetApiUsagePanel totalCalls={50000} endpoints={30} unused={2} topEndpoint="/health" />);
    expect(container.textContent).toContain("API Usage");
    expect(container.textContent).toContain("/health");
}); });
