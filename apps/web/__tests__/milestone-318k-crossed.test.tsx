import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone318kCrossed } from "@/components/milestone-318k-crossed";
describe("Milestone318kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone318kCrossed />);
    expect(container.textContent).toContain("318K CROSSED");
}); });
