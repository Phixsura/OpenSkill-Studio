import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudBillingV9Panel } from "@/components/fleet-cloud-billing-v9-panel";
describe("FleetCloudBillingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudBillingV9Panel accounts={3} spend={150000} />);
    expect(container.textContent).toContain("Cloud Billing v9");
}); });
