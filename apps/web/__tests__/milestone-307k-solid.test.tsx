import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone307kSolid } from "@/components/milestone-307k-solid";
describe("Milestone307kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone307kSolid />);
    expect(container.textContent).toContain("307K+");
}); });
