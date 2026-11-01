import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3500Commits } from "@/components/milestone-3500-commits";
describe("Milestone3500Commits", () => { it("renders", () => {
    const { container } = render(<Milestone3500Commits />);
    expect(container.textContent).toContain("3,500 COMMITS");
    expect(container.textContent).toContain("UNSTOPPABLE");
}); });
