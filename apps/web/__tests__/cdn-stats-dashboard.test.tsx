import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CdnStatsDashboard } from "@/components/cdn-stats-dashboard";

describe("CdnStatsDashboard", () => {
  it("renders stats", () => {
    const stats = { totalAssets: 150, totalSizeBytes: 5242880, totalBandwidth: 1073741824, edgeLocations: 6 };
    const { container } = render(<CdnStatsDashboard stats={stats} />);
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("5.0 MB");
    expect(container.textContent).toContain("1.0 GB");
    expect(container.textContent).toContain("6");
  });
});
