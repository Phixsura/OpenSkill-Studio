import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone310kCrossed } from "@/components/milestone-310k-crossed";
describe("Milestone310kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone310kCrossed />);
    expect(container.textContent).toContain("310K CROSSED");
}); });
