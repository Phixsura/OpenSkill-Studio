import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatsHero } from "@/components/platform-stats-hero";

describe("PlatformStatsHero", () => {
  it("renders stats", () => {
    const stats = [
      { label: "Apps", value: 500, icon: "📦" },
      { label: "Developers", value: 100, icon: "👨‍💻" },
      { label: "Installs", value: 25000, icon: "📥" },
    ];
    const { container } = render(
      <PlatformStatsHero stats={stats} title="OpenSkill Marketplace" subtitle="Build. Share. Grow." />
    );
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("25,000");
    expect(container.textContent).toContain("Build. Share. Grow.");
  });
});
