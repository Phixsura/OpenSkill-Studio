import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InvoiceView } from "@/components/invoice-view";

describe("InvoiceView", () => {
  it("renders invoice", () => {
    const { container } = render(
      <InvoiceView invoiceId="INV-ABC123" orgName="Acme Corp" plan="pro"
        period="October 2026" subtotalDisplay="$149.00" taxDisplay="$14.90"
        totalDisplay="$163.90" status="paid"
        items={[
          { description: "Pro Plan", quantity: 1, amountDisplay: "$99.00" },
          { description: "API Overage", quantity: 50, amountDisplay: "$50.00" },
        ]} />
    );
    expect(container.textContent).toContain("Invoice");
    expect(container.textContent).toContain("INV-ABC123");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("Pro Plan");
    expect(container.textContent).toContain("$163.90");
    expect(container.textContent).toContain("paid");
  });
});
