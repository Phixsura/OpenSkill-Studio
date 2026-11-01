import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone323kFinal } from "@/components/milestone-323k-final";
describe("Milestone323kFinal", () => { it("renders", () => {
    const { container } = render(<Milestone323kFinal />);
    expect(container.textContent).toContain("323K OFFICIALLY CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
