import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-850th-pair-milestone-card";

describe("850thPairMilestoneCard", () => {
  it("shows milestone", () => {
    const stats = { total_pairs: 850, total_commits: 1092, total_tests: 5950, total_files: 3400, security_fixes: 40 };
    const { container } = render(<Card stats={stats} tier="LEGENDARY x4" appName="OpenSkill" />);
    expect(container.textContent).toContain("LEGENDARY x4");
    expect(container.textContent).toContain("850");
    expect(container.textContent).toContain("1,092");
    expect(container.textContent).toContain("5,950");
  });
  it("shows tier", () => {
    const stats = { total_pairs: 850, total_commits: 1092, total_tests: 5950, total_files: 3400, security_fixes: 40 };
    const { container } = render(<Card stats={stats} tier="LEGENDARY x4" appName="App" />);
    expect(container.textContent).toContain("LEGENDARY");
  });
});
