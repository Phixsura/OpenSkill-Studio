import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnomalyScorePanel } from "@/components/anomaly-score-panel";

describe("AnomalyScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <AnomalyScorePanel mean={15} std={25} threshold={3} total={10}
        anomalies={[{ index: 9, value: 100, zScore: 3.4 }]} />
    );
    expect(container.textContent).toContain("Anomaly Detection");
    expect(container.textContent).toContain("1 anomalies");
    expect(container.textContent).toContain("10 points");
    expect(container.textContent).toContain("Index 9");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("3.4");
  });
});
