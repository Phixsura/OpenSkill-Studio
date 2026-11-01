import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone298kCrossed } from "@/components/milestone-298k-crossed";
describe("Milestone298kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone298kCrossed />);
    expect(container.textContent).toContain("298K CROSSED");
    expect(container.textContent).toContain("2K TO 300K");
}); });
