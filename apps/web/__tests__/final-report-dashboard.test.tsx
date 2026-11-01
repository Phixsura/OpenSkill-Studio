import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalReportDashboard } from "@/components/final-report-dashboard";

const report = {
  scale: { total: 675, backend: 294, frontend: 381, tests: 3190, commits: 4860, security: 47 },
  quality: { passRate: 100, dora: "elite" },
  modules: ["Extension SDK", "Sandboxed Apps", "Connector Marketplace", "Automation API", "Third-party Ecosystem"],
  achievements: ["🏆 600+ Services", "✅ 3,000+ Tests GREEN", "🚀 DORA Elite"],
};

describe("FinalReportDashboard", () => {
  it("renders the complete final report", () => {
    const { container } = render(<FinalReportDashboard report={report} />);
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("675");
    expect(container.textContent).toContain("3,190");
    expect(container.textContent).toContain("4,860");
    expect(container.textContent).toContain("elite");
    expect(container.textContent).toContain("600+ Services");
    expect(container.textContent).toContain("100%");
  });
});
