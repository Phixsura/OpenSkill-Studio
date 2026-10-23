import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BillingAlertManager } from "@/components/billing-alert-manager";

describe("BillingAlertManager", () => {
  const alerts = [{ alert_id: "al1", type: "monthly_spend", threshold: 100, status: "active", notify_channels: ["email"] }];
  const triggered = [{ alert_id: "al1", type: "monthly_spend", current: 120, threshold: 100, severity: "warning", exceeded_by_pct: 20 }];
  it("renders", () => {
    const { container } = render(
      <BillingAlertManager alerts={alerts} triggered={triggered} onDelete={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Billing Alerts");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("+20%");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <BillingAlertManager alerts={alerts} triggered={[]} onDelete={fn} onCreate={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete")!);
    expect(fn).toHaveBeenCalledWith("al1");
  });
});
