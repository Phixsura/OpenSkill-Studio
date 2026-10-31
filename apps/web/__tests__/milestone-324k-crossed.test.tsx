import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone324kCrossed } from "@/components/milestone-324k-crossed";
describe("Milestone324kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone324kCrossed />);
    expect(container.textContent).toContain("324K CROSSED");
    expect(container.textContent).toContain("+21,251");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
