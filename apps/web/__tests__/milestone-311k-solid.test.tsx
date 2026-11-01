import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone311kSolid } from "@/components/milestone-311k-solid";
describe("Milestone311kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone311kSolid />);
    expect(container.textContent).toContain("311K+");
}); });
