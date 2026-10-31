import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone285kLinesPanel } from "@/components/milestone-285k-lines-panel";
describe("Milestone285kLinesPanel", () => { it("renders", () => {
    const { container } = render(<Milestone285kLinesPanel />);
    expect(container.textContent).toContain("285,000+ Lines");
}); });
