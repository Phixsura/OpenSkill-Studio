import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone14kFiles } from "@/components/milestone-14k-files";
describe("Milestone14kFiles", () => { it("renders", () => {
    const { container } = render(<Milestone14kFiles />);
    expect(container.textContent).toContain("14,000");
    expect(container.textContent).toContain("FOURTEEN THOUSAND");
}); });
