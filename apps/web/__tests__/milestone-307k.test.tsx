import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone307k } from "@/components/milestone-307k";
describe("Milestone307k", () => { it("renders", () => {
    const { container } = render(<Milestone307k />);
    expect(container.textContent).toContain("307K");
}); });
