import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone289k } from "@/components/milestone-289k";
describe("Milestone289k", () => { it("renders", () => {
    const { container } = render(<Milestone289k />);
    expect(container.textContent).toContain("289,000 Lines");
}); });
