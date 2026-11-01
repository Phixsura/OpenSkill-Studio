import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PayoutDashboard } from "@/components/payout-dashboard";

const mockPayouts = [
  { id: "p1", grossCents: 10000, taxCents: 1000, netCents: 9000,
    status: "completed" as const, paymentMethod: "stripe", reference: "ref-1", createdAt: "2024-01-15" },
  { id: "p2", grossCents: 5000, taxCents: 500, netCents: 4500,
    status: "pending" as const, paymentMethod: "paypal", createdAt: "2024-02-01" },
];

describe("PayoutDashboard", () => {
  it("renders balance and totals", () => {
    const { container } = render(
      <PayoutDashboard payouts={mockPayouts} balanceCents={8500} thresholdCents={5000} />
    );
    expect(container.textContent).toContain("$85.00");
    expect(container.textContent).toContain("$50.00");
    expect(container.textContent).toContain("$90.00"); // total paid
  });

  it("enables payout when above threshold", () => {
    const onRequest = vi.fn();
    const { getByText } = render(
      <PayoutDashboard payouts={[]} balanceCents={10000} thresholdCents={5000} onRequestPayout={onRequest} />
    );
    fireEvent.click(getByText("Request Payout"));
    expect(onRequest).toHaveBeenCalled();
  });

  it("disables payout below threshold", () => {
    const { container } = render(
      <PayoutDashboard payouts={[]} balanceCents={2000} thresholdCents={5000} />
    );
    expect(container.textContent).toContain("Need $30.00 more");
  });

  it("shows payout history", () => {
    const { container } = render(
      <PayoutDashboard payouts={mockPayouts} balanceCents={0} thresholdCents={5000} />
    );
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("stripe");
  });
});
