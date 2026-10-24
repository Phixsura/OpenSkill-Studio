import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceQuotaV9Panel } from "@/components/fleet-service-quota-v9-panel";
describe("FleetServiceQuotaV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceQuotaV9Panel quotas={50} nearLimit={2} />);
    expect(container.textContent).toContain("Service Quota v9");
}); });
