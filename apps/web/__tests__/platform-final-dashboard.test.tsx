import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformFinalDashboard } from "@/components/platform-final-dashboard";

const summary = {
  scale: { services: 620, backend: 276, frontend: 344, tests: 3000, commits: 4841, securityFixes: 47 },
  quality: { testPassRate: 100, uptime: 99.99, errorRate: 0.1, avgResponseMs: 42 },
  growth: { developers: 2000, extensions: 500, installs: 100000, mrrCents: 5000000 },
  dora: "elite",
};
const achievements = ["🏆 600+ Services Built", "✅ 3,000+ Tests GREEN", "🚀 DORA Elite Performance"];

describe("PlatformFinalDashboard", () => {
  it("renders the complete platform dashboard", () => {
    const { container } = render(<PlatformFinalDashboard summary={summary} achievements={achievements} />);
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("620");
    expect(container.textContent).toContain("3,000");
    expect(container.textContent).toContain("4,841");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("elite");
    expect(container.textContent).toContain("600+ Services Built");
    expect(container.textContent).toContain("DORA Elite Performance");
  });
});
