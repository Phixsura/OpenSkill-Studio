import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone302kCrossed } from "@/components/milestone-302k-crossed";
describe("Milestone302kCrossed", () => { it("renders", () => {
    const { container } = render(<Milestone302kCrossed />);
    expect(container.textContent).toContain("302K");
}); });
