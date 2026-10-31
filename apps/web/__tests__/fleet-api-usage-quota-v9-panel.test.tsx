import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiUsageQuotaV9Panel } from "@/components/fleet-api-usage-quota-v9-panel";
describe("FleetApiUsageQuotaV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiUsageQuotaV9Panel consumers={100} overQuota={0} />);
    expect(container.textContent).toContain("API Usage Quota v9");
}); });
