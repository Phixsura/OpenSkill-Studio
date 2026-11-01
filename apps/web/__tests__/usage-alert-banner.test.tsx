import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UsageAlertBanner } from "@/components/usage-alert-banner";

describe("UsageAlertBanner", () => {
  it("shows warning", () => {
    const alerts = [{ resource: "api_calls", usage_pct: 85, level: "warning" as const, current: 8500, limit: 10000 }];
    const { container } = render(<UsageAlertBanner alerts={alerts} />);
    expect(container.textContent).toContain("Usage Warning");
    expect(container.textContent).toContain("85%");
  });
  it("shows critical", () => {
    const alerts = [{ resource: "storage", usage_pct: 98, level: "critical" as const, current: 980, limit: 1000 }];
    const { container } = render(<UsageAlertBanner alerts={alerts} />);
    expect(container.textContent).toContain("Usage Critical");
  });
  it("hidden when no alerts", () => {
    const { container } = render(<UsageAlertBanner alerts={[]} />);
    expect(container.innerHTML).toBe("");
  });
  it("upgrade button", () => {
    const fn = vi.fn();
    const alerts = [{ resource: "x", usage_pct: 99, level: "critical" as const, current: 99, limit: 100 }];
    const { container } = render(<UsageAlertBanner alerts={alerts} onUpgrade={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
