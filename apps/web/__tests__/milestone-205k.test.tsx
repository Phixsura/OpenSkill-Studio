import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone205k } from "@/components/milestone-205k";

describe("Milestone205k", () => {
  it("renders celebration", () => {
    const { container } = render(
      <Milestone205k achievement="🏆🏆🏆 205K!!!"
        stats={{ commits: 2356, lines: 205000, files: 6804 }} />
    );
    expect(container.textContent).toContain("205,000 LINES");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
    expect(container.textContent).toContain("2,356");
    expect(container.textContent).toContain("6,804");
  });
});
