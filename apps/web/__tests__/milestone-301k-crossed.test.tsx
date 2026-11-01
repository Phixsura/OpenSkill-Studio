import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone301kCrossed } from "@/components/milestone-301k-crossed";
describe("Milestone301kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone301kCrossed />);
    expect(container.textContent).toContain("301K");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
