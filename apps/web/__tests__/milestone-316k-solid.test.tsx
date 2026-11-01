import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone316kSolid } from "@/components/milestone-316k-solid";
describe("Milestone316kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone316kSolid />);
    expect(container.textContent).toContain("316K+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
