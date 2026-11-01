import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3600Commits } from "@/components/milestone-3600-commits";
describe("Milestone3600Commits", () => { it("renders", () => {
    const { container } = render(<Milestone3600Commits />);
    expect(container.textContent).toContain("3,600");
}); });
