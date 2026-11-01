import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone316kCrossed } from "@/components/milestone-316k-crossed";
describe("Milestone316kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone316kCrossed />);
    expect(container.textContent).toContain("316K CROSSED");
}); });
