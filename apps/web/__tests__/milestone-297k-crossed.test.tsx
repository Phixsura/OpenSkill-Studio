import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone297kCrossed } from "@/components/milestone-297k-crossed";
describe("Milestone297kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone297kCrossed />);
    expect(container.textContent).toContain("297K CROSSED");
    expect(container.textContent).toContain("3K TO 300K");
}); });
