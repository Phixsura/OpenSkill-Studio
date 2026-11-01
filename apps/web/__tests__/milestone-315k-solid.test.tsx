import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone315kSolid } from "@/components/milestone-315k-solid";
describe("Milestone315kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone315kSolid />);
    expect(container.textContent).toContain("315K+");
}); });
