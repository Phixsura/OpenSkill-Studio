import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone304kSolid } from "@/components/milestone-304k-solid";
describe("Milestone304kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone304kSolid />);
    expect(container.textContent).toContain("304K+");
    expect(container.textContent).toContain("305K");
}); });
