import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone240kHero } from "@/components/milestone-240k-hero";

describe("Milestone240kHero", () => {
  it("renders", () => {
    const { container } = render(<Milestone240kHero />);
    expect(container.textContent).toContain("240K Lines");
    expect(container.textContent).toContain("2,784");
    expect(container.textContent).toContain("8,228+");
    expect(container.textContent).toContain("1,392+");
    expect(container.textContent).toContain("ALL SYSTEMS GREEN");
    expect(container.textContent).toContain("Fully Operational");
  });
});
