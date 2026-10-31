import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone315kCrossed } from "@/components/milestone-315k-crossed";
describe("Milestone315kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone315kCrossed />);
    expect(container.textContent).toContain("315K CROSSED");
}); });
