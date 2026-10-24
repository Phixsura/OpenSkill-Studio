import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone296kCrossed } from "@/components/milestone-296k-crossed";
describe("Milestone296kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone296kCrossed />);
    expect(container.textContent).toContain("296K Lines Crossed");
}); });
