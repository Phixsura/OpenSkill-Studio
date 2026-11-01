import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CicdMetricsDashboard } from "@/components/cicd-metrics-dashboard";

describe("CicdMetricsDashboard", () => {
  it("renders metrics", () => {
    const { container } = render(
      <CicdMetricsDashboard totalRuns={500} passRate={95} avgDurationSec={180}
        p95DurationSec={350} deploysPerDay={3.5} doraLevel="elite" />
    );
    expect(container.textContent).toContain("CI/CD Metrics");
    expect(container.textContent).toContain("DORA: elite");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("3.5");
    expect(container.textContent).toContain("180s");
    expect(container.textContent).toContain("350s");
  });
});
