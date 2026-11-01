import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3800Commits } from "@/components/milestone-3800-commits";
describe("Milestone3800Commits", () => { it("renders", () => {
    const { container } = render(<Milestone3800Commits />);
    expect(container.textContent).toContain("3,800");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
