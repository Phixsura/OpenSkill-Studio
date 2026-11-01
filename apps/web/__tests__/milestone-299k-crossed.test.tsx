import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone299kCrossed } from "@/components/milestone-299k-crossed";
describe("Milestone299kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone299kCrossed />);
    expect(container.textContent).toContain("299K CROSSED");
    expect(container.textContent).toContain("FINAL 1,000");
}); });
