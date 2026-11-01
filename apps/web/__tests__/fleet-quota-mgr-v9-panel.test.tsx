import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQuotaMgrV9Panel } from "@/components/fleet-quota-mgr-v9-panel";
describe("FleetQuotaMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetQuotaMgrV9Panel tenants={100} overQuota={0} />);
    expect(container.textContent).toContain("Quota Manager v9");
}); });
