import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone299kCrossedFinal } from "@/components/milestone-299k-crossed-final";
describe("Milestone299kCrossedFinal", () => { it("renders", () => {
    const { container } = render(<Milestone299kCrossedFinal />);
    expect(container.textContent).toContain("299K CROSSED");
    expect(container.textContent).toContain("300,000");
}); });
