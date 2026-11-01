import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone298kCrossedFinal } from "@/components/milestone-298k-crossed-final";
describe("Milestone298kCrossedFinal", () => { it("renders", () => {
    const { container } = render(<Milestone298kCrossedFinal />);
    expect(container.textContent).toContain("UNDER 2K TO 300K");
}); });
