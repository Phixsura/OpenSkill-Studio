import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthTimelineChart } from "@/components/health-timeline-chart";

describe("HealthTimelineChart", () => {
  it("renders", () => {
    const timeline = [
      { timestamp: "2026-01-01", status: "healthy", response_ms: 100 },
      { timestamp: "2026-01-02", status: "down", response_ms: 0 },
    ];
    const { container } = render(<HealthTimelineChart timeline={timeline} uptimePct={99.95} currentStatus="healthy" />);
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("90 days ago");
    expect(container.querySelector("[class*='bg-green']")).toBeTruthy();
  });
});
