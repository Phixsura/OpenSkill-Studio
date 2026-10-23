import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SparklineWidget } from "@/components/sparkline-widget";

describe("SparklineWidget", () => {
  it("renders", () => {
    const { container } = render(
      <SparklineWidget points={[20, 40, 60, 80, 100]} label="Installs"
        current={500} change={50} changePct={11.1} trend="up" />
    );
    expect(container.textContent).toContain("Installs");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("↑ 11.1%");
  });
  it("down trend", () => {
    const { container } = render(
      <SparklineWidget points={[100, 80, 60]} label="Users"
        current={300} change={-20} changePct={-6.3} trend="down" />
    );
    expect(container.textContent).toContain("↓ 6.3%");
  });
});
