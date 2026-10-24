import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3390 } from "@/components/milestone-3390";
describe("Milestone3390", () => { it("renders", () => {
    const { container } = render(<Milestone3390 />);
    expect(container.textContent).toContain("3,390 Commits");
}); });
