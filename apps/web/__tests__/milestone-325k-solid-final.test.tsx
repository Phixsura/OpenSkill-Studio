import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone325kSolidFinal } from "@/components/milestone-325k-solid-final";
describe("Milestone325kSolidFinal", () => { it("renders", () => {
    const { container } = render(<Milestone325kSolidFinal />);
    expect(container.textContent).toContain("325K+ SOLID");
    expect(container.textContent).toContain("QUARTER MILLION");
    expect(container.textContent).toContain("+22,251");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
