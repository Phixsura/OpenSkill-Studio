import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone320kSolid } from "@/components/milestone-320k-solid";
describe("Milestone320kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone320kSolid />);
    expect(container.textContent).toContain("320K+");
}); });
