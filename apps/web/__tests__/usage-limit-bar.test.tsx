import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UsageLimitBar } from "@/components/usage-limit-bar";

describe("UsageLimitBar", () => {
  it("renders limits", () => {
    const onUpgrade = vi.fn();
    const { container, getByText } = render(
      <UsageLimitBar plan="free" exceeded={true} nextPlan="starter" onUpgrade={onUpgrade}
        checks={[
          { resource: "apps", used: 5, limit: 3, pct: 100, ok: false },
          { resource: "api_calls_daily", used: 500, limit: 1000, pct: 50, ok: true },
        ]} />
    );
    expect(container.textContent).toContain("Plan Limits");
    expect(container.textContent).toContain("free");
    expect(container.textContent).toContain("5 / 3");
    expect(container.textContent).toContain("Upgrade to starter");
    fireEvent.click(getByText(/Upgrade/));
    expect(onUpgrade).toHaveBeenCalled();
  });
});
