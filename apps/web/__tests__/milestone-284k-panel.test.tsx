import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone284kPanel } from "@/components/milestone-284k-panel";
describe("Milestone284kPanel", () => { it("renders", () => {
    const { container } = render(<Milestone284kPanel />);
    expect(container.textContent).toContain("284,000 Lines");
}); });
