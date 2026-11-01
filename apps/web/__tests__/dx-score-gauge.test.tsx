import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DxScoreGauge } from "@/components/dx-score-gauge";

describe("DxScoreGauge", () => {
  it("renders gauge", () => {
    const { container } = render(
      <DxScoreGauge score={92} grade="A" display="92/100 (A)" />
    );
    expect(container.textContent).toContain("Developer Experience");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92/100");
  });
});
