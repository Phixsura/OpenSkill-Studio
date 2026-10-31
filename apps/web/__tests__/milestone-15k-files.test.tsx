import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone15kFiles } from "@/components/milestone-15k-files";
describe("Milestone15kFiles", () => { it("renders", () => {
    const { container } = render(<Milestone15kFiles />);
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("FIFTEEN THOUSAND");
}); });
