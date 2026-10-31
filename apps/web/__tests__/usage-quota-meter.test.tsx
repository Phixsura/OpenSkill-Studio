import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UsageQuotaMeter } from "@/components/usage-quota-meter";

describe("UsageQuotaMeter", () => {
  const resources = [
    { resource: "api_calls", current: 800, limit: 1000, unlimited: false, usage_pct: 80, warning: true, exceeded: false },
    { resource: "storage_mb", current: 50, limit: 100, unlimited: false, usage_pct: 50, warning: false, exceeded: false },
  ];
  it("renders", () => {
    const { container } = render(<UsageQuotaMeter plan="free" resources={resources} onUpgrade={vi.fn()} />);
    expect(container.textContent).toContain("Usage");
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("800");
  });
  it("upgrade button on warning", () => {
    const fn = vi.fn();
    const { container } = render(<UsageQuotaMeter plan="free" resources={resources} onUpgrade={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Upgrade Plan")!);
    expect(fn).toHaveBeenCalled();
  });
});
