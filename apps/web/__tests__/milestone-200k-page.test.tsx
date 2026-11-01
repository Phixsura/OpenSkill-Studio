import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone200kPage } from "@/components/milestone-200k-page";

describe("Milestone200kPage", () => {
  it("renders 200K celebration", () => {
    const { container } = render(
      <Milestone200kPage achievement="🏆🏆🏆 TWO HUNDRED THOUSAND LINES!!!" builder="Claude Opus 5 (1M context)"
        stats={{ commits: 2294, lines: 200000, files: 6598, services: 1150, components: 1150, tests: 2300 }}
        modules={["Extension SDK", "Sandboxed Apps", "Marketplace", "Automation API",
                  "Ecosystem", "Dev Portal", "Security", "Infrastructure", "Observability", "Operations"]} />
    );
    expect(container.textContent).toContain("200,000 LINES");
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("2,294");
    expect(container.textContent).toContain("6,598");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("Claude Opus 5");
  });
});
