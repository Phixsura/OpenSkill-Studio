import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceStatsDashboard } from "@/components/marketplace-stats-dashboard";

describe("MarketplaceStatsDashboard", () => {
  it("renders full dashboard", () => {
    const { container } = render(
      <MarketplaceStatsDashboard
        codebase={{ commits: 1855, lines: 163000, files: 5170 }}
        marketplace={{ totalApps: 5200, totalDevelopers: 1800, totalDownloads: 12500000, avgRating: 4.6 }}
        infra={{ uptimePct: 99.99, avgResponseMs: 45, regions: 6 }}
        modules={["Extension SDK", "Marketplace"]}
        achievement="🏆 1,855 commits!" />
    );
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("1,855");
    expect(container.textContent).toContain("163K");
    expect(container.textContent).toContain("5,200");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("Extension SDK");
  });
});
