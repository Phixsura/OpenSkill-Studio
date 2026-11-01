import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone270K } from "@/components/milestone-270k";
describe("Milestone270K", () => {
  it("renders", () => {
    const { container } = render(<Milestone270K />);
    expect(container.textContent).toContain("270,000 Lines");
    expect(container.textContent).toContain("3,186 commits");
    expect(container.textContent).toContain("ALL OPERATIONAL");
  });
});
