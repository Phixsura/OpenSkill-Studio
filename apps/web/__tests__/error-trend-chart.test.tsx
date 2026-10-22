import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorTrendChart } from "@/components/error-trend-chart";

describe("ErrorTrendChart", () => {
  it("shows rising", () => {
    const { container } = render(<ErrorTrendChart trend="rising" avg={25} peak={100} criticalCount={3} />);
    expect(container.textContent).toContain("Rising");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("3");
  });
  it("shows stable", () => {
    const { container } = render(<ErrorTrendChart trend="stable" avg={2} peak={5} criticalCount={0} />);
    expect(container.textContent).toContain("Stable");
  });
});
