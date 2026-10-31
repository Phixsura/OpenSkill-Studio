import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOverviewPage } from "@/components/platform-overview-page";

describe("PlatformOverviewPage", () => {
  const modules = [{ name: "Extension SDK", status: "✅", services: 150 }];
  const stats = { commits: 1850, lines: 163000, files: 5150, services: 1000, components: 900, tests: 1900 };
  it("renders platform overview", () => {
    const { container } = render(
      <PlatformOverviewPage platform="OpenSkill" version="6.0.0" status="OPERATIONAL"
        modules={modules} stats={stats} achievement="🏆 1,850 commits!" />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("6.0.0");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("1,850");
    expect(container.textContent).toContain("🏆");
  });
});
