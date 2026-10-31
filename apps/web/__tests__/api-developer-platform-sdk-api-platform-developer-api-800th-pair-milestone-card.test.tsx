import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-800th-pair-milestone-card";

describe("800thPairMilestoneCard", () => {
  it("shows milestone", () => {
    const stats = { total_pairs: 800, total_commits: 1040, backend_tests: 4000, frontend_tests: 1600, security_fixes: 35 };
    const { container } = render(<Card stats={stats} tier="LEGENDARY x3" appName="OpenSkill" />);
    expect(container.textContent).toContain("LEGENDARY x3");
    expect(container.textContent).toContain("800");
    expect(container.textContent).toContain("1,040");
    expect(container.textContent).toContain("4,000");
  });
  it("shows tier", () => {
    const stats = { total_pairs: 800, total_commits: 1040, backend_tests: 4000, frontend_tests: 1600, security_fixes: 35 };
    const { container } = render(<Card stats={stats} tier="LEGENDARY x3" appName="App" />);
    expect(container.textContent).toContain("LEGENDARY");
  });
});
