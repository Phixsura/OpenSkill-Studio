import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone298kFinal } from "@/components/milestone-298k-final";
describe("Milestone298kFinal", () => { it("renders", () => {
    const { container } = render(<Milestone298kFinal />);
    expect(container.textContent).toContain("298K");
    expect(container.textContent).toContain("ALMOST THERE");
}); });
