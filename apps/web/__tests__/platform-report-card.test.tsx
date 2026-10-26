import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformReportCard } from "@/components/platform-report-card";

const report = {
  platform: { services: 585, backend: 264, frontend: 321, tests: 2880, commits: 4832 },
  quality: { testPassRate: 100, avgLatencyMs: 45, errorRate: 0.3, uptime: 99.99 },
  growth: { developers: 2000, extensions: 500, installs: 100000 },
  dora: { classification: "elite", deploymentFrequency: "multiple_per_day",
          leadTime: "less_than_hour", changeFailure: "less_than_5pct", timeToRestore: "less_than_hour" },
};

describe("PlatformReportCard", () => {
  it("renders full platform report", () => {
    const { container } = render(<PlatformReportCard report={report} />);
    expect(container.textContent).toContain("585");
    expect(container.textContent).toContain("2,880");
    expect(container.textContent).toContain("4,832");
    expect(container.textContent).toContain("elite");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("99.99%");
  });
});
