import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResourceQuotaV9Panel } from "@/components/fleet-resource-quota-v9-panel";
describe("FleetResourceQuotaV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetResourceQuotaV9Panel quotas={20} cpuUsed={50} />);
    expect(container.textContent).toContain("Resource Quota v9");
}); });
