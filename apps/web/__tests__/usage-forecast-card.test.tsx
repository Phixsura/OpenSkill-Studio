import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UsageForecastCard } from "@/components/usage-forecast-card";

describe("UsageForecastCard", () => {
  it("renders ok", () => {
    const { container } = render(
      <UsageForecastCard resource="api_calls" currentUsage={7000} limit={10000}
        daysUntilBreach={15} urgency="ok" dailyGrowth={200} onUpgrade={vi.fn()} />
    );
    expect(container.textContent).toContain("api calls");
    expect(container.textContent).toContain("On track");
    expect(container.textContent).toContain("~15 days left");
    expect(container.textContent).toContain("+200/day");
  });
  it("critical shows upgrade", () => {
    const { container } = render(
      <UsageForecastCard resource="storage" currentUsage={9500} limit={10000}
        daysUntilBreach={2} urgency="critical" dailyGrowth={300} onUpgrade={vi.fn()} />
    );
    expect(container.textContent).toContain("Limit imminent");
    expect(container.textContent).toContain("Upgrade");
  });
});
