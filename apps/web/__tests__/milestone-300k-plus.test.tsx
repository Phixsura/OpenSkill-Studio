import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone300kPlus } from "@/components/milestone-300k-plus";
describe("Milestone300kPlus", () => { it("renders", () => {
    const { container } = render(<Milestone300kPlus />);
    expect(container.textContent).toContain("300K+");
}); });
