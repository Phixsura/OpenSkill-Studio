import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatsHero } from "@/components/platform-stats-hero";

describe("PlatformStatsHero", () => {
  it("renders stats", () => {
    const { container } = render(
      <PlatformStatsHero commits={2580} lines={222000} files={7486}
        services={1290} components={1290} modules={10} />
    );
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("2,580");
    expect(container.textContent).toContain("222K");
    expect(container.textContent).toContain("7,486");
    expect(container.textContent).toContain("10");
  });
});
