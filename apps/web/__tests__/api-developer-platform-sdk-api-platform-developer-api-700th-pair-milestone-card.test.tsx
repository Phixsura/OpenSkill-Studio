import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-700th-pair-milestone-card";

describe("700thPairMilestoneCard", () => {
  it("shows milestone", () => {
    const stats = { total_pairs: 700, total_commits: 928, total_backend_tests: 3500, total_frontend_tests: 1400, security_fixes: 15 };
    const { container } = render(<Card stats={stats} milestoneTitle="LEGENDARY x2!" appName="OpenSkill Studio" />);
    expect(container.textContent).toContain("LEGENDARY x2!");
    expect(container.textContent).toContain("700");
    expect(container.textContent).toContain("928");
    expect(container.textContent).toContain("15 security fixes");
  });
  it("shows without fixes", () => {
    const stats = { total_pairs: 1, total_commits: 1, total_backend_tests: 5, total_frontend_tests: 2, security_fixes: 0 };
    const { container } = render(<Card stats={stats} milestoneTitle="First!" appName="App" />);
    expect(container.textContent).toContain("First!");
    expect(container.textContent).not.toContain("security fixes");
  });
});
