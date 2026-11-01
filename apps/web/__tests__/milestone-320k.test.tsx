import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone320k } from "@/components/milestone-320k";
describe("Milestone320k", () => { it("renders", () => {
    const { container } = render(<Milestone320k />);
    expect(container.textContent).toContain("320,000");
    expect(container.textContent).toContain("THREE HUNDRED TWENTY THOUSAND");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
