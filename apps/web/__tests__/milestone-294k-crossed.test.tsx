import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone294kCrossed } from "@/components/milestone-294k-crossed";
describe("Milestone294kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone294kCrossed />);
    expect(container.textContent).toContain("294K");
}); });
