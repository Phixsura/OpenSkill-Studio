import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalyticsSparkline } from "@/components/analytics-sparkline";

describe("AnalyticsSparkline", () => {
  it("renders svg", () => {
    const { container } = render(<AnalyticsSparkline data={[1, 3, 2, 5, 4]} />);
    expect(container.querySelector("svg")).toBeTruthy();
    expect(container.querySelector("polyline")).toBeTruthy();
  });
  it("empty data returns null", () => {
    const { container } = render(<AnalyticsSparkline data={[]} />);
    expect(container.querySelector("svg")).toBeNull();
  });
});
