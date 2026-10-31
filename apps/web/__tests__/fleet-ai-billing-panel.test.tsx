import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBillingPanel } from "@/components/fleet-ai-billing-panel";
describe("FleetAiBillingPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBillingPanel meters={3} active={3} revenue={200000} invoices={5000} customers={2000} />);
    expect(container.textContent).toContain("AI Billing");
}); });
