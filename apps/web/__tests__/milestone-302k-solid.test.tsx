import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone302kSolid } from "@/components/milestone-302k-solid";
describe("Milestone302kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone302kSolid />);
    expect(container.textContent).toContain("302K+");
}); });
