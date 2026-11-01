import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogAnomalyCard } from "@/components/log-anomaly-card";

describe("LogAnomalyCard", () => {
  it("renders", () => {
    const { container } = render(
      <LogAnomalyCard mean={100} std={10} checked={7} hasAnomaly={true}
        anomalies={[{ index: 4, count: 500, zScore: 40, type: "spike" }]} />
    );
    expect(container.textContent).toContain("Log Anomalies");
    expect(container.textContent).toContain("1 detected");
    expect(container.textContent).toContain("Period 4");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("z=40");
  });
});
