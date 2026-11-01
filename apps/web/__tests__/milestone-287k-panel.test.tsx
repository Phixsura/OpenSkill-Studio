import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone287kPanel } from "@/components/milestone-287k-panel";
describe("Milestone287kPanel", () => { it("renders", () => {
    const { container } = render(<Milestone287kPanel />);
    expect(container.textContent).toContain("287,000 Lines");
}); });
