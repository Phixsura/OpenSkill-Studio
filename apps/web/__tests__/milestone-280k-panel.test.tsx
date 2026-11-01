import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone280kPanel } from "@/components/milestone-280k-panel";
describe("Milestone280kPanel", () => { it("renders", () => {
    const { container } = render(<Milestone280kPanel />);
    expect(container.textContent).toContain("280,000 Lines");
}); });
