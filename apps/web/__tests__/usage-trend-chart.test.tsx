import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageTrendChart } from "@/components/usage-trend-chart";

describe("UsageTrendChart", () => {
  it("renders trends", () => {
    const { container } = render(
      <UsageTrendChart trend="growing" changePct={45.5} avg={155} peak={250}
        trough={100} dataPoints={8} volatility={96.8} />
    );
    expect(container.textContent).toContain("Usage Trends");
    expect(container.textContent).toContain("growing");
    expect(container.textContent).toContain("+45.5%");
    expect(container.textContent).toContain("250");
    expect(container.textContent).toContain("8 data points");
  });
});
