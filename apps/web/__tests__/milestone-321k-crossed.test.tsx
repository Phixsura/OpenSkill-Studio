import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone321kCrossed } from "@/components/milestone-321k-crossed";
describe("Milestone321kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone321kCrossed />);
    expect(container.textContent).toContain("321K CROSSED");
}); });
