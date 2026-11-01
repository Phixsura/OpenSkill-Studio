import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone322k } from "@/components/milestone-322k";
describe("Milestone322k", () => { it("renders", () => {
    const { container } = render(<Milestone322k />);
    expect(container.textContent).toContain("322K");
}); });
