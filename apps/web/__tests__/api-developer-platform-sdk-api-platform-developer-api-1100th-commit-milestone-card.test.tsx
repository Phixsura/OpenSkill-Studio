import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-1100th-commit-milestone-card";

describe("1100thMilestoneCard", () => {
  it("shows milestone", () => {
    const stats = { total_commits: 1100, total_pairs: 858, total_tests: 6006, total_files: 3432, security_fixes: 40 };
    const { container } = render(<Card stats={stats} tier="BEYOND ETERNAL x1.1" appName="OpenSkill" />);
    expect(container.textContent).toContain("BEYOND ETERNAL x1.1");
    expect(container.textContent).toContain("1,100");
    expect(container.textContent).toContain("858");
    expect(container.textContent).toContain("6,006");
  });
  it("shows security fixes", () => {
    const stats = { total_commits: 1100, total_pairs: 858, total_tests: 6006, total_files: 3432, security_fixes: 40 };
    const { container } = render(<Card stats={stats} tier="BEYOND ETERNAL x1.1" appName="App" />);
    expect(container.textContent).toContain("40 security fixes");
  });
});
