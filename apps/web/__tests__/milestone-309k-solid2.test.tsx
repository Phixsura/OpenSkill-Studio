import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone309kSolid2 } from "@/components/milestone-309k-solid2";
describe("Milestone309kSolid2", () => { it("renders", () => {
    const { container } = render(<Milestone309kSolid2 />);
    expect(container.textContent).toContain("309K+");
}); });
