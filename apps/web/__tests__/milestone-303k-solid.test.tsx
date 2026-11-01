import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone303kSolid } from "@/components/milestone-303k-solid";
describe("Milestone303kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone303kSolid />);
    expect(container.textContent).toContain("303K+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
