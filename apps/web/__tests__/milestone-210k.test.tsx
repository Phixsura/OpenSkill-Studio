import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone210k } from "@/components/milestone-210k";

describe("Milestone210k", () => {
  it("renders 210K", () => {
    const { container } = render(
      <Milestone210k commits={2417} lines={210000} files={7018}
        achievements={["200K crossed", "7K files", "2400 commits"]} />
    );
    expect(container.textContent).toContain("210,000 LINES");
    expect(container.textContent).toContain("2,417");
    expect(container.textContent).toContain("7,018");
    expect(container.textContent).toContain("200K crossed");
    expect(container.textContent).toContain("FULLY OPERATIONAL");
  });
});
