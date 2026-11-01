import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone324kSolid } from "@/components/milestone-324k-solid";
describe("Milestone324kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone324kSolid />);
    expect(container.textContent).toContain("324K+ SOLID");
    expect(container.textContent).toContain("+21,251");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
