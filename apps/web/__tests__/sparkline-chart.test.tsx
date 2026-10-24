import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SparklineChart } from "@/components/sparkline-chart";

describe("SparklineChart", () => {
  it("renders sparkline", () => {
    const { container } = render(
      <SparklineChart polyline="0,24 50,12 100,0" width={100} height={24}
        trend="up" current={30} changePct={200} label="Revenue" />
    );
    expect(container.textContent).toContain("Revenue");
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("+200%");
    expect(container.querySelector("svg")).toBeTruthy();
    expect(container.querySelector("polyline")).toBeTruthy();
  });
});
