import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatsHero } from "@/components/platform-stats-hero";

describe("PlatformStatsHero", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformStatsHero commits={1475} lines={130000} files={3861}
        services={850} components={750} tests={1700} version="5.5.0" />
    );
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("v5.5.0");
    expect(container.textContent).toContain("1,475");
    expect(container.textContent).toContain("130,000");
    expect(container.textContent).toContain("3,861");
    expect(container.textContent).toContain("🏆");
  });
});
