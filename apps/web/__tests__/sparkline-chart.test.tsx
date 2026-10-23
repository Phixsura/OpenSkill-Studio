import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SparklineChart } from "@/components/sparkline-chart";

describe("SparklineChart", () => {
  it("renders svg path", () => {
    const { container } = render(
      <SparklineChart points={[0, 50, 100, 75]} label="Downloads" current={75} trend="down" />
    );
    expect(container.querySelector("svg")).toBeTruthy();
    expect(container.querySelector("path")).toBeTruthy();
    expect(container.textContent).toContain("75");
    expect(container.textContent).toContain("Downloads");
  });
  it("handles < 2 points", () => {
    const { container } = render(
      <SparklineChart points={[50]} label="" current={50} trend="flat" />
    );
    expect(container.textContent).toContain("—");
  });
});
