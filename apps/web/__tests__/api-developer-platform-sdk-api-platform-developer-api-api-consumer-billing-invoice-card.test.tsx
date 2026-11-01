import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-billing-invoice-card";

describe("BillingInvoiceCard", () => {
  it("shows invoices", () => {
    const invoices = [{ invoice_id: "inv-1", consumer_id: "c1", period: "2024-01", status: "issued", total_dollars: "$125.00", line_count: 2 }];
    const { container } = render(<Card invoices={invoices} outstandingTotal="$125.00" appName="App" />);
    expect(container.textContent).toContain("Billing");
    expect(container.textContent).toContain("$125.00 due");
    expect(container.textContent).toContain("2024-01");
    expect(container.textContent).toContain("issued");
  });
  it("shows empty", () => {
    const { container } = render(<Card invoices={[]} outstandingTotal="$0.00" appName="App" />);
    expect(container.textContent).toContain("No invoices");
  });
});
