import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone283kPanel } from "@/components/milestone-283k-panel";
describe("Milestone283kPanel", () => { it("renders", () => {
    const { container } = render(<Milestone283kPanel />);
    expect(container.textContent).toContain("283,000 Lines");
}); });
