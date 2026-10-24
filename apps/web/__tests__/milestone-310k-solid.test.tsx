import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone310kSolid } from "@/components/milestone-310k-solid";
describe("Milestone310kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone310kSolid />);
    expect(container.textContent).toContain("310K+");
}); });
