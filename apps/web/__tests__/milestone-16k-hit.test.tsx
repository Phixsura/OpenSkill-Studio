import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone16kHit } from "@/components/milestone-16k-hit";
describe("Milestone16kHit", () => { it("renders", () => {
    const { container } = render(<Milestone16kHit />);
    expect(container.textContent).toContain("16,000 FILES");
    expect(container.textContent).toContain("SIXTEEN THOUSAND");
}); });
