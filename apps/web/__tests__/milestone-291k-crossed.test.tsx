import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone291kCrossed } from "@/components/milestone-291k-crossed";
describe("Milestone291kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone291kCrossed />);
    expect(container.textContent).toContain("291K Lines Crossed");
}); });
