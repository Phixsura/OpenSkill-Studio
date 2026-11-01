import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EarningsDashboard } from "@/components/earnings-dashboard";

describe("EarningsDashboard", () => {
  it("renders earnings", () => {
    const { container } = render(
      <EarningsDashboard grossCents={10000} netCents={8500} feePct={15} balanceCents={8500} payoutEligible={true} onRequestPayout={vi.fn()} />
    );
    expect(container.textContent).toContain("$100.00");
    expect(container.textContent).toContain("$85.00");
    expect(container.textContent).toContain("Request Payout");
  });
  it("not eligible", () => {
    const { container } = render(
      <EarningsDashboard grossCents={3000} netCents={2550} feePct={15} balanceCents={2550} payoutEligible={false} onRequestPayout={vi.fn()} />
    );
    expect(container.textContent).toContain("until payout");
  });
  it("request payout", () => {
    const fn = vi.fn();
    const { container } = render(
      <EarningsDashboard grossCents={10000} netCents={8500} feePct={15} balanceCents={8500} payoutEligible={true} onRequestPayout={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
