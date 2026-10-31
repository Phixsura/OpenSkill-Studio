import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone313k } from "@/components/milestone-313k";
describe("Milestone313k", () => { it("renders", () => {
    const { container } = render(<Milestone313k />);
    expect(container.textContent).toContain("313K");
}); });
