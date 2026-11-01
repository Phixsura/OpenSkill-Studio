import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone295kCrossed } from "@/components/milestone-295k-crossed";
describe("Milestone295kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone295kCrossed />);
    expect(container.textContent).toContain("295K Lines Crossed");
}); });
