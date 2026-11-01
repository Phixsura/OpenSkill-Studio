import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiUsageBillingCalculatorCard from "../src/components/api-developer-api-api-usage-billing-calculator-card";

const invoice = {
  invoice_id: "inv-1", period: "2025-01",
  line_items: [{ description: "API Calls", quantity: 100000, total_cents: 100000 }],
  subtotal_cents: 100000, discount_cents: 10000, total_cents: 90000,
};

describe("APIDeveloperAPIApiUsageBillingCalculatorCard", () => {
  it("shows billing", () => {
    const { container } = render(<APIDeveloperAPIApiUsageBillingCalculatorCard invoice={invoice} appName="App" />);
    expect(container.textContent).toContain("Usage Billing");
    expect(container.textContent).toContain("2025-01");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("100,000");
    expect(container.textContent).toContain("$900.00");
    expect(container.textContent).toContain("Discount");
  });
});
