import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone290kCrossed } from "@/components/milestone-290k-crossed";
describe("Milestone290kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone290kCrossed />);
    expect(container.textContent).toContain("290K LINES CROSSED");
    expect(container.textContent).toContain("300,000");
}); });
