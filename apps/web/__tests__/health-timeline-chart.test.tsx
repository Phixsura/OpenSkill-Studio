import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthTimelineChart } from "@/components/health-timeline-chart";

describe("HealthTimelineChart", () => {
  it("renders timeline", () => {
    const { container } = render(
      <HealthTimelineChart uptimePct={90} incidents={1} windowHours={24} improving={true}
        timeline={[{ healthy: true }, { healthy: true }, { healthy: false }, { healthy: true }]} />
    );
    expect(container.textContent).toContain("Health Timeline (24h)");
    expect(container.textContent).toContain("90% uptime");
    expect(container.textContent).toContain("1 incidents");
  });
});
