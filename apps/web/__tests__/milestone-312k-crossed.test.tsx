import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone312kCrossed } from "@/components/milestone-312k-crossed";
describe("Milestone312kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone312kCrossed />);
    expect(container.textContent).toContain("312K CROSSED");
}); });
