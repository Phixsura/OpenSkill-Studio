import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone309kSolid } from "@/components/milestone-309k-solid";
describe("Milestone309kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone309kSolid />);
    expect(container.textContent).toContain("309K+");
    expect(container.textContent).toContain("310K");
}); });
