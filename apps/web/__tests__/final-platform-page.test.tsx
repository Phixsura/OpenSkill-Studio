import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalPlatformPage } from "@/components/final-platform-page";

describe("FinalPlatformPage", () => {
  it("renders the grand finale", () => {
    const { container } = render(
      <FinalPlatformPage platform="OpenSkill" version="12.0.0" status="OPERATIONAL"
        stats={{ commits: 1950, lines: 171600, files: 5504 }} modules={10}
        highlights={["Complete marketplace", "170K+ lines"]}
        achievement="🏆 1,950 commits!" />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("1,950");
    expect(container.textContent).toContain("172K");
    expect(container.textContent).toContain("5,504");
    expect(container.textContent).toContain("10 Platform Modules");
    expect(container.textContent).toContain("Complete marketplace");
  });
});
