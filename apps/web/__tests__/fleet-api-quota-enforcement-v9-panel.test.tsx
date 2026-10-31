import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiQuotaEnforcementV9Panel } from "@/components/fleet-api-quota-enforcement-v9-panel";
describe("FleetApiQuotaEnforcementV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiQuotaEnforcementV9Panel consumers={100} exceeded={0} />);
    expect(container.textContent).toContain("Quota Enforcement v9");
}); });
