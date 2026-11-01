import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone16kCrossed } from "@/components/milestone-16k-crossed";
describe("Milestone16kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone16kCrossed />);
    expect(container.textContent).toContain("16,000 FILES CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
