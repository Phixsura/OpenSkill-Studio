import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCustomerV7Panel } from "@/components/fleet-ai-customer-v7-panel";
describe("FleetAiCustomerV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCustomerV7Panel systems={3} active={3} customers={200000} csat={4.9} nps={80} churn={1.5} />);
    expect(container.textContent).toContain("Customer v7");
}); });
