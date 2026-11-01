import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone325kCrossed } from "@/components/milestone-325k-crossed";
describe("Milestone325kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone325kCrossed />);
    expect(container.textContent).toContain("325K CROSSED");
    expect(container.textContent).toContain("QUARTER MILLION");
    expect(container.textContent).toContain("NEVER STOPS");
    expect(container.textContent).toContain("+22,251");
}); });
