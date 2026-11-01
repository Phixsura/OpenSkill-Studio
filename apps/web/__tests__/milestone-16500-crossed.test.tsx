import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone16500Crossed } from "@/components/milestone-16500-crossed";
describe("Milestone16500Crossed", () => { it("renders", () => {
    const { container } = render(<Milestone16500Crossed />);
    expect(container.textContent).toContain("16,500 FILES CROSSED");
}); });
