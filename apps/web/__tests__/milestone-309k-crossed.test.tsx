import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone309kCrossed } from "@/components/milestone-309k-crossed";
describe("Milestone309kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone309kCrossed />);
    expect(container.textContent).toContain("309K CROSSED");
}); });
