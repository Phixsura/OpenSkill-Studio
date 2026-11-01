import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UltimatePlatformSummary } from "@/components/ultimate-platform-summary";

describe("UltimatePlatformSummary", () => {
  it("renders summary", () => {
    const { container } = render(
      <UltimatePlatformSummary platform="OpenSkill" version="ULTIMATE" status="OPERATIONAL"
        codebase={{ commits: 2024, lines: 177000, files: 5752, backendServices: 1015, frontendComponents: 1000 }}
        pagesBuilt={["Landing", "Dashboard"]} integrations={["GitHub", "Slack"]} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("2,024");
    expect(container.textContent).toContain("177,000");
    expect(container.textContent).toContain("2 Pages Built");
    expect(container.textContent).toContain("GitHub");
  });
});
