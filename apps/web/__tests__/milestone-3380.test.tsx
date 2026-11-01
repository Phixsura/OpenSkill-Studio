import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3380 } from "@/components/milestone-3380";
describe("Milestone3380", () => { it("renders", () => {
    const { container } = render(<Milestone3380 />);
    expect(container.textContent).toContain("3,380 Commits");
}); });
