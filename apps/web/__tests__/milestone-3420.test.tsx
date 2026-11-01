import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3420 } from "@/components/milestone-3420";
describe("Milestone3420", () => { it("renders", () => {
    const { container } = render(<Milestone3420 />);
    expect(container.textContent).toContain("3,420");
}); });
