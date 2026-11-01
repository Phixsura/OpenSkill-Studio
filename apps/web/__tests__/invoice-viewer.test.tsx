import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InvoiceViewer } from "@/components/invoice-viewer";

describe("InvoiceViewer", () => {
  it("renders invoice", () => {
    const { container } = render(
      <InvoiceViewer invoiceId="INV-ABC123" customer="Acme Corp" subtotal={119}
        tax={11.9} total={130.9} displayTotal="$130.90"
        lineItems={[
          { description: "API Pro Plan", quantity: 1, unitPrice: 99, total: 99 },
          { description: "Extra Storage", quantity: 2, unitPrice: 10, total: 20 },
        ]} />
    );
    expect(container.textContent).toContain("INV-ABC123");
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("$130.90");
    expect(container.textContent).toContain("API Pro Plan");
    expect(container.textContent).toContain("$99.00");
    expect(container.textContent).toContain("Subtotal");
  });
});
