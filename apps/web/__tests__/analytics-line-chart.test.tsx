import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsLineChart } from "@/components/analytics-line-chart";

describe("AnalyticsLineChart", () => {
  it("renders chart", () => {
    const { container } = render(
      <AnalyticsLineChart labels={["Jan 1", "Jan 2", "Jan 3"]} values={[10, 25, 15]}
        metric="installs" total={50} average={16.7} peak={25} trend="up" />
    );
    expect(container.textContent).toContain("installs");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("Jan 1");
  });
});
