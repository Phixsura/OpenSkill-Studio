import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BillingPage } from "@/components/billing-page";

describe("BillingPage", () => {
  it("renders billing", () => {
    const { container } = render(
      <BillingPage orgName="Acme" plan={{ name: "Pro", price: 29, interval: "monthly", apiLimit: 500000 }}
        usage={{ apiCalls: 600000, apiPct: 120, storageMb: 512 }}
        billing={{ base: 29, overage: 100, total: 129 }}
        payment={{ brand: "Visa", last4: "4242" }}
        invoices={[{ id: "inv_1", amount: 29, status: "paid", date: "2026-01-01" }]}
        onUpgrade={vi.fn()} onManagePayment={vi.fn()} />
    );
    expect(container.textContent).toContain("Billing — Acme");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("$129.00");
    expect(container.textContent).toContain("120%");
    expect(container.textContent).toContain("4242");
    expect(container.textContent).toContain("Overage");
  });
});
