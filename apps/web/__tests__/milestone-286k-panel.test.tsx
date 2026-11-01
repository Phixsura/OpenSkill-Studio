import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone286kPanel } from "@/components/milestone-286k-panel";
describe("Milestone286kPanel", () => { it("renders", () => {
    const { container } = render(<Milestone286kPanel />);
    expect(container.textContent).toContain("286,000 Lines");
}); });
