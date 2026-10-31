import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageBillingPanel } from "@/components/usage-billing-panel";

const mockEndpoints = [
  { endpoint: "/api/data", calls: 15000, bytes: 5242880 },
  { endpoint: "/api/search", calls: 3000, bytes: 1048576 },
];
const mockInvoices = [
  { id: "i1", periodStart: "Jan 2024", periodEnd: "Jan 2024", totalCalls: 25000, totalCostCents: 150, status: "paid" },
];

describe("UsageBillingPanel", () => {
  it("renders usage stats", () => {
    const { container } = render(
      <UsageBillingPanel endpoints={mockEndpoints} invoices={mockInvoices}
        totalCalls={18000} estimatedCostCents={80} freeTierRemaining={2000} />
    );
    expect(container.textContent).toContain("18,000");
    expect(container.textContent).toContain("$0.80");
    expect(container.textContent).toContain("2,000");
  });

  it("shows endpoint usage", () => {
    const { container } = render(
      <UsageBillingPanel endpoints={mockEndpoints} invoices={[]}
        totalCalls={0} estimatedCostCents={0} freeTierRemaining={0} />
    );
    expect(container.textContent).toContain("/api/data");
    expect(container.textContent).toContain("15,000 calls");
  });

  it("shows invoices tab", () => {
    const { getByText, container } = render(
      <UsageBillingPanel endpoints={mockEndpoints} invoices={mockInvoices}
        totalCalls={0} estimatedCostCents={0} freeTierRemaining={0} />
    );
    fireEvent.click(getByText("Invoices (1)"));
    expect(container.textContent).toContain("Jan 2024");
    expect(container.textContent).toContain("$1.50");
  });
});
