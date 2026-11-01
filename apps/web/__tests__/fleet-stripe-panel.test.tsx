import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStripePanel } from "@/components/fleet-stripe-panel";
describe("FleetStripePanel", () => { it("renders", () => {
    const { container } = render(<FleetStripePanel accounts={3} active={3} volume={1500000} successRate={99.5} />);
    expect(container.textContent).toContain("Stripe");
    expect(container.textContent).toContain("99.5%");
}); });
