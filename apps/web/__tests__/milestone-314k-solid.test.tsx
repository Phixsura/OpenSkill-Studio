import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone314kSolid } from "@/components/milestone-314k-solid";
describe("Milestone314kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone314kSolid />);
    expect(container.textContent).toContain("314K+");
    expect(container.textContent).toContain("315K");
}); });
