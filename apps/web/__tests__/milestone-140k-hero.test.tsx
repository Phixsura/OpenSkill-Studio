import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone140kHero } from "@/components/milestone-140k-hero";

describe("Milestone140kHero", () => {
  const stats = { commits: 1586, lines: 140000, files: 4267,
    backend_services: 960, frontend_components: 860, test_files: 1950, security_fixes: 9 };
  it("renders the celebration", () => {
    const { container } = render(
      <Milestone140kHero stats={stats} achievement="🎉 140K!" version="10.0.0"
        codename="One Hundred Forty Thousand" tech={["Python", "React"]} journey="Amazing journey" />
    );
    expect(container.textContent).toContain("140,000 LINES!");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("v10.0.0");
    expect(container.textContent).toContain("1,586");
    expect(container.textContent).toContain("140,000");
    expect(container.textContent).toContain("4,267");
    expect(container.textContent).toContain("Python · React");
    expect(container.textContent).toContain("🎉 140K!");
  });
});
