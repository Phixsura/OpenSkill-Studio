import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone323kSolid } from "@/components/milestone-323k-solid";
describe("Milestone323kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone323kSolid />);
    expect(container.textContent).toContain("323K+");
    expect(container.textContent).toContain("+20,251");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
