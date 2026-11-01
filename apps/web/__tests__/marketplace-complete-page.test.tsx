import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MarketplaceCompletePage } from "@/components/marketplace-complete-page";

describe("MarketplaceCompletePage", () => {
  it("renders complete page", () => {
    const { container } = render(
      <MarketplaceCompletePage platform="OpenSkill" version="9.0.0" status="OPERATIONAL"
        achievement="🏆 1,900 commits!"
        codebase={{ commits: 1900, lines: 167000, files: 5330, backendServices: 950, frontendComponents: 900, testFiles: 1900 }}
        modules={{ extension_sdk: { status: "operational", services: 150 } }}
        milestones={["150K lines", "1,900 commits"]} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("1,900");
    expect(container.textContent).toContain("167,000");
    expect(container.textContent).toContain("extension sdk");
    expect(container.textContent).toContain("150K lines");
  });
});
