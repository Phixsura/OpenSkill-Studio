import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuotaUsagePanel } from "@/components/quota-usage-panel";

describe("QuotaUsagePanel", () => {
  it("renders quotas", () => {
    const quotas = [
      { resource: "apps", current: 3, limit: 5, unlimited: false },
      { resource: "api_calls", current: 999, limit: -1, unlimited: true },
    ];
    const { container } = render(<QuotaUsagePanel plan="starter" quotas={quotas} onUpgrade={vi.fn()} />);
    expect(container.textContent).toContain("starter");
    expect(container.textContent).toContain("3 / 5");
    expect(container.textContent).toContain("999 / ∞");
  });
});
