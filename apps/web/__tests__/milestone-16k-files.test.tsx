import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone16kFiles } from "@/components/milestone-16k-files";
describe("Milestone16kFiles", () => { it("renders", () => {
    const { container } = render(<Milestone16kFiles />);
    expect(container.textContent).toContain("16,000");
    expect(container.textContent).toContain("SIXTEEN THOUSAND");
}); });
