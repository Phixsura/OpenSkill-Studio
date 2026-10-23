import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourceUsageTimelineChart } from "@/components/resource-usage-timeline-chart";

describe("ResourceUsageTimelineChart", () => {
  const stats = {
    cpu: { peak: 80, avg: 50, current: 45 },
    memory: { peak: 90, avg: 65, current: 70 },
  };
  it("renders", () => {
    const { container } = render(
      <ResourceUsageTimelineChart resources={["cpu", "memory"]} stats={stats} totalPoints={100} />
    );
    expect(container.textContent).toContain("Resource Usage");
    expect(container.textContent).toContain("100 data points");
    expect(container.textContent).toContain("🖥️");
    expect(container.textContent).toContain("Current: 45%");
    expect(container.textContent).toContain("Peak: 80%");
    expect(container.textContent).toContain("💾");
    expect(container.textContent).toContain("Current: 70%");
  });
});
