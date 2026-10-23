import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EarningsPageLayout } from "@/components/earnings-page-layout";

describe("EarningsPageLayout", () => {
  it("renders", () => {
    const { container } = render(
      <EarningsPageLayout summary={{ gross: "$150.00", net: "$127.50", fee_pct: 15 }}
        payouts={{ pending_cents: 8000, total_payouts: 3 }} hasTaxInfo={true}
        onRequestPayout={vi.fn()} onAddTaxInfo={vi.fn()}>
        <p>Transactions</p>
      </EarningsPageLayout>
    );
    expect(container.textContent).toContain("$150.00");
    expect(container.textContent).toContain("$127.50");
    expect(container.textContent).toContain("Request Payout");
    expect(container.textContent).toContain("Transactions");
  });
  it("no tax info warning", () => {
    const { container } = render(
      <EarningsPageLayout summary={{ gross: "$0", net: "$0", fee_pct: 15 }}
        payouts={{ pending_cents: 0, total_payouts: 0 }} hasTaxInfo={false}
        onRequestPayout={vi.fn()} onAddTaxInfo={vi.fn()}>
        <p>C</p>
      </EarningsPageLayout>
    );
    expect(container.textContent).toContain("Tax information required");
  });
});
