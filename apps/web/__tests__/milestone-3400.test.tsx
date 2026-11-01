import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3400 } from "@/components/milestone-3400";
describe("Milestone3400", () => { it("renders", () => {
    const { container } = render(<Milestone3400 />);
    expect(container.textContent).toContain("3,400 Commits");
    expect(container.textContent).toContain("UNSTOPPABLE");
}); });
