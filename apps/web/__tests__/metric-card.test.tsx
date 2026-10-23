import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricCard } from "@/components/metric-card";

describe("MetricCard", () => {
  it("renders metric with trend", () => {
    const { container } = render(
      <MetricCard label="Users" display="1,234" unit="total" trend="up" changePct={25.5} />
    );
    expect(container.textContent).toContain("Users");
    expect(container.textContent).toContain("1,234");
    expect(container.textContent).toContain("total");
    expect(container.textContent).toContain("25.5%");
    expect(container.textContent).toContain("↑");
  });
  it("no trend", () => {
    const { container } = render(
      <MetricCard label="Revenue" display="$5,000.00" unit="" trend={null} changePct={null} />
    );
    expect(container.textContent).toContain("$5,000.00");
    expect(container.textContent).not.toContain("vs prev");
  });
});
