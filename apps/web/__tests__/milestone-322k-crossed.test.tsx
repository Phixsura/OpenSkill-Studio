import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone322kCrossed } from "@/components/milestone-322k-crossed";
describe("Milestone322kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone322kCrossed />);
    expect(container.textContent).toContain("322K CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
