import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone317kCrossed } from "@/components/milestone-317k-crossed";
describe("Milestone317kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone317kCrossed />);
    expect(container.textContent).toContain("317K CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
