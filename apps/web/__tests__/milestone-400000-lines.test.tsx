import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone400000Lines } from "@/components/milestone-400000-lines";
describe("Milestone400000Lines", () => { it("renders", () => {
    const { container } = render(<Milestone400000Lines />);
    expect(container.textContent).toContain("400,000");
    expect(container.textContent).toContain("FOUR HUNDRED THOUSAND");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
