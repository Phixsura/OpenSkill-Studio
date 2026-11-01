import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-950th-commit-milestone-card";

describe("950thMilestoneCard", () => {
  it("shows milestone", () => {
    const stats = { total_commits: 950, total_pairs: 717, backend_tests: 3585, frontend_tests: 1434, security_fixes: 20 };
    const { container } = render(<Card stats={stats} currentMilestone="APPROACHING ETERNAL" nextMilestone={1000} progressPct={0} appName="OpenSkill" />);
    expect(container.textContent).toContain("APPROACHING ETERNAL");
    expect(container.textContent).toContain("950");
    expect(container.textContent).toContain("717");
    expect(container.textContent).toContain("1000");
  });
  it("shows progress", () => {
    const stats = { total_commits: 975, total_pairs: 730, backend_tests: 3650, frontend_tests: 1460, security_fixes: 22 };
    const { container } = render(<Card stats={stats} currentMilestone="APPROACHING ETERNAL" nextMilestone={1000} progressPct={50} appName="App" />);
    expect(container.textContent).toContain("975");
  });
});
