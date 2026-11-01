import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthTrendCard } from "@/components/health-trend-card";

describe("HealthTrendCard", () => {
  it("renders trends", () => {
    const trends = [
      { metric: "Latency", trend: "degrading", change_pct: 25 },
      { metric: "Errors", trend: "improving", change_pct: -30 },
    ];
    const { container } = render(<HealthTrendCard trends={trends} overall="degrading" needsAttention={true} />);
    expect(container.textContent).toContain("Latency");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("degrading");
  });
});
