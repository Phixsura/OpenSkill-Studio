import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone308kSolid } from "@/components/milestone-308k-solid";
describe("Milestone308kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone308kSolid />);
    expect(container.textContent).toContain("308K+");
}); });
