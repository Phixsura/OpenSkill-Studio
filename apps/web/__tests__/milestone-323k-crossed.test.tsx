import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone323kCrossed } from "@/components/milestone-323k-crossed";
describe("Milestone323kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone323kCrossed />);
    expect(container.textContent).toContain("323K CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
