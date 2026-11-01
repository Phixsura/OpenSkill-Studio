import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GrowthTracker } from "@/components/growth-tracker";

describe("GrowthTracker", () => {
  it("renders", () => {
    const { container } = render(
      <GrowthTracker overall="growing" periods={2}
        metrics={{
          users: { first: 1000, last: 1500, growthPct: 50, trend: "up" },
          revenue: { first: 5000, last: 7500, growthPct: 50, trend: "up" },
        }} />
    );
    expect(container.textContent).toContain("Platform Growth");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("+50%");
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("1,000 → 1,500");
  });
});
