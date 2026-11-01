import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BillingSummaryCard } from "@/components/billing-summary-card";

const ITEMS = [{ item: "Executions", qty: 1000, rate: 0.001, cost: 1.0 }, { item: "API Calls", qty: 5000, rate: 0.00005, cost: 0.25 }];

describe("BillingSummaryCard", () => {
  it("shows total", () => {
    const { container } = render(<BillingSummaryCard items={ITEMS} totalUsd={1.25} tier="standard" />);
    expect(container.textContent).toContain("$1.25");
  });
  it("shows items", () => {
    const { container } = render(<BillingSummaryCard items={ITEMS} totalUsd={1.25} tier="standard" />);
    expect(container.textContent).toContain("Executions");
  });
  it("shows tier", () => {
    const { container } = render(<BillingSummaryCard items={ITEMS} totalUsd={0} tier="premium" />);
    expect(container.textContent).toContain("premium");
  });
});
