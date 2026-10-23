import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FinalSummaryPage } from "@/components/final-summary-page";

describe("FinalSummaryPage", () => {
  it("renders summary", () => {
    const { container } = render(
      <FinalSummaryPage platform="OpenSkill" version="8.0.0" status="OPERATIONAL"
        achievement="🏆 166K lines!" codebase={{ commits: 1890, lines: 166000, files: 5290 }}
        modules={{ "Extension SDK": "✅ Operational" }}
        milestones={["150K lines", "5,000 files"]} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("1,890");
    expect(container.textContent).toContain("166K");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("150K lines");
  });
});
