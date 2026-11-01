import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone325k } from "@/components/milestone-325k";
describe("Milestone325k", () => { it("renders", () => {
    const { container } = render(<Milestone325k />);
    expect(container.textContent).toContain("325K");
    expect(container.textContent).toContain("QUARTER MILLION");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
