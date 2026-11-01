import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOverviewHero } from "@/components/platform-overview-hero";

describe("PlatformOverviewHero", () => {
  const modules = { marketplace: { status: "operational", version: "3.5" },
    security: { status: "operational", version: "3.0" } };
  const stats = { total_commits: 1350, total_files: 3415, total_lines: 116000,
    backend_services: 780, frontend_components: 660 };
  it("renders", () => {
    const { container } = render(
      <PlatformOverviewHero platformName="OpenSkill" version="4.0.0" status="operational"
        modules={modules} stats={stats} milestones={["100K lines"]} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("v4.0.0");
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("1,350");
    expect(container.textContent).toContain("3,415");
    expect(container.textContent).toContain("marketplace");
  });
});
