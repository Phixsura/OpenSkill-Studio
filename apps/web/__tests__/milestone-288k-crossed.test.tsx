import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone288kCrossed } from "@/components/milestone-288k-crossed";
describe("Milestone288kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone288kCrossed />);
    expect(container.textContent).toContain("288K Lines Crossed");
}); });
