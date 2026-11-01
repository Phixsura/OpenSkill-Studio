import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3350Panel } from "@/components/milestone-3350-panel";
describe("Milestone3350Panel", () => { it("renders", () => {
    const { container } = render(<Milestone3350Panel />);
    expect(container.textContent).toContain("3,350 Commits");
}); });
