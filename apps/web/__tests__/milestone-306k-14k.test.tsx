import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone306k14k } from "@/components/milestone-306k-14k";
describe("Milestone306k14k", () => { it("renders", () => {
    const { container } = render(<Milestone306k14k />);
    expect(container.textContent).toContain("306K");
    expect(container.textContent).toContain("14K");
    expect(container.textContent).toContain("DOUBLE MILESTONE");
}); });
