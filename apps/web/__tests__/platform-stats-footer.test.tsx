import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatsFooter } from "@/components/platform-stats-footer";

describe("PlatformStatsFooter", () => {
  it("renders footer", () => {
    const { container } = render(
      <PlatformStatsFooter commits={2375} lines={206600} files={6872}
        services={1188} modules={10} status="FULLY OPERATIONAL" />
    );
    expect(container.textContent).toContain("2,375 commits");
    expect(container.textContent).toContain("206,600 lines");
    expect(container.textContent).toContain("6,872 files");
    expect(container.textContent).toContain("10 modules");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("Claude Opus 5");
  });
});
