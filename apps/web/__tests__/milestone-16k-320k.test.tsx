import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone16k320k } from "@/components/milestone-16k-320k";
describe("Milestone16k320k", () => { it("renders", () => {
    const { container } = render(<Milestone16k320k />);
    expect(container.textContent).toContain("16K");
    expect(container.textContent).toContain("320K");
}); });
