import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone16k320kImminent } from "@/components/milestone-16k-320k-imminent";
describe("Milestone16k320kImminent", () => { it("renders", () => {
    const { container } = render(<Milestone16k320kImminent />);
    expect(container.textContent).toContain("16K FILES");
    expect(container.textContent).toContain("320K");
}); });
