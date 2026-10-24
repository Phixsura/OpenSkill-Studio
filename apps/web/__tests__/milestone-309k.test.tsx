import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone309k } from "@/components/milestone-309k";
describe("Milestone309k", () => { it("renders", () => {
    const { container } = render(<Milestone309k />);
    expect(container.textContent).toContain("309K");
}); });
