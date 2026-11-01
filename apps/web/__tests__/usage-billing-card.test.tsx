import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageBillingCard } from "@/components/usage-billing-card";

const bill = {
  items: [
    { metric: "api_calls", quantity: 1000, unitPrice: 1, total: 1000 },
    { metric: "storage_mb", quantity: 50, unitPrice: 5, total: 250 },
  ],
  totalCents: 1250,
};

describe("UsageBillingCard", () => {
  it("renders bill", () => {
    const { container } = render(<UsageBillingCard bill={bill} />);
    expect(container.textContent).toContain("$12.50");
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("storage mb");
    expect(container.textContent).toContain("$10.00");
  });
  it("empty state", () => {
    const { container } = render(<UsageBillingCard bill={{ items: [], totalCents: 0 }} />);
    expect(container.textContent).toContain("No usage");
  });
});
