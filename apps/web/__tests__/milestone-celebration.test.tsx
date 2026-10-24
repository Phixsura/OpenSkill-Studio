import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneCelebration } from "@/components/milestone-celebration";

describe("MilestoneCelebration", () => {
  const stats = { commits: 1387, lines: 120000, files: 3537, services: 800, components: 700, tests: 1600 };
  const modules = ["Extension SDK", "Marketplace", "Security"];
  it("renders", () => {
    const { container } = render(
      <MilestoneCelebration milestone="120,000 LINES" achievement="🎉 120K!"
        stats={stats} modules={modules} />
    );
    expect(container.textContent).toContain("120,000 LINES");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("1,387");
    expect(container.textContent).toContain("120,000");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("3 platform modules");
  });
});
