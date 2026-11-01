import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthTrendIndicator } from "@/components/health-trend-indicator";

describe("HealthTrendIndicator", () => {
  it("shows improving", () => {
    const { container } = render(<HealthTrendIndicator trend="improving" current={95} change={5} />);
    expect(container.textContent).toContain("📈");
    expect(container.textContent).toContain("+5");
  });
  it("shows declining", () => {
    const { container } = render(<HealthTrendIndicator trend="declining" current={80} change={-10} />);
    expect(container.textContent).toContain("📉");
    expect(container.textContent).toContain("-10");
  });
  it("shows stable", () => {
    const { container } = render(<HealthTrendIndicator trend="stable" current={95} change={0} />);
    expect(container.textContent).toContain("➡️");
  });
});
