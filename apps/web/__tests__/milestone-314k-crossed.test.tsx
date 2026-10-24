import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone314kCrossed } from "@/components/milestone-314k-crossed";
describe("Milestone314kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone314kCrossed />);
    expect(container.textContent).toContain("314K CROSSED");
}); });
