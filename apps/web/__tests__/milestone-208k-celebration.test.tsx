import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone208kCelebration } from "@/components/milestone-208k-celebration";

describe("Milestone208kCelebration", () => {
  it("renders celebration", () => {
    const { container } = render(
      <Milestone208kCelebration achievement="🏆🏆🏆 208K!!!"
        stats={{ commits: 2391, lines: 208000, files: 6928, services: 1196 }}
        milestones={["180K → 208K lines", "2,000 → 2,391 commits"]} />
    );
    expect(container.textContent).toContain("208,000 LINES");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("2,391");
    expect(container.textContent).toContain("6,928");
    expect(container.textContent).toContain("180K → 208K");
  });
});
