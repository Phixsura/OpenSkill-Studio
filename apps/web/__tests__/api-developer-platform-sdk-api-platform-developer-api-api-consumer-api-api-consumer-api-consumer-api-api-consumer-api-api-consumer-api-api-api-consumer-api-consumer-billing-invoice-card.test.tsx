import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-consumer-billing-invoice-card";

describe("ConsumerBillingInvoiceCard", () => {
  it("shows invoices", () => {
    const invoices = [{ id: "inv1", period: "2026-06", status: "paid", totalCents: 16500, lineItems: [{ description: "API Calls", quantity: 10000, totalCents: 10000 }] }];
    const { container } = render(<Card invoices={invoices} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Billing Invoices");
    expect(container.textContent).toContain("2026-06");
    expect(container.textContent).toContain("$165.00");
    expect(container.textContent).toContain("paid");
  });
  it("shows empty", () => {
    const { container } = render(<Card invoices={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No invoices");
  });
});
