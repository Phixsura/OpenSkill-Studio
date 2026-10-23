import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricCard } from "@/components/metric-card";

describe("MetricCard", () => {
  it("renders with change", () => {
    const { container } = render(
      <MetricCard label="Users" value={1500} change={300} changePct={25}
        trend="up" formatType="number" icon="👥" />
    );
    expect(container.textContent).toContain("Users");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("↑ 300");
    expect(container.textContent).toContain("+25%");
    expect(container.textContent).toContain("👥");
  });
  it("renders currency", () => {
    const { container } = render(
      <MetricCard label="Revenue" value={5000} change={null} changePct={null}
        trend={null} formatType="currency" icon="💰" />
    );
    expect(container.textContent).toContain("$5,000");
  });
});
