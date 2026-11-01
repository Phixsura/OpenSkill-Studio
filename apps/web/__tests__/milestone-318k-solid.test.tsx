import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone318kSolid } from "@/components/milestone-318k-solid";
describe("Milestone318kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone318kSolid />);
    expect(container.textContent).toContain("318K+");
    expect(container.textContent).toContain("319K");
}); });
