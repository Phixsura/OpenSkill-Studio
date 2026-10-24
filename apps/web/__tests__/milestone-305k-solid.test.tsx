import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone305kSolid } from "@/components/milestone-305k-solid";
describe("Milestone305kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone305kSolid />);
    expect(container.textContent).toContain("305K+");
}); });
