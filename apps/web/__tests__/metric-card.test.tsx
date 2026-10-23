import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricCard } from "@/components/metric-card";

describe("MetricCard", () => {
  it("renders card", () => {
    const { container } = render(
      <MetricCard label="Revenue" display="$45,000" icon="💰"
        deltaDisplay="+12.5%" trend="up" unit="" />
    );
    expect(container.textContent).toContain("$45,000");
    expect(container.textContent).toContain("Revenue");
    expect(container.textContent).toContain("+12.5%");
    expect(container.textContent).toContain("↑");
  });
});
