import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPagesPanel } from "@/components/fleet-pages-panel";
describe("FleetPagesPanel", () => { it("renders", () => {
    const { container } = render(<FleetPagesPanel projects={20} deployed={20} builds={100} customDomains={40} />);
    expect(container.textContent).toContain("Pages");
}); });
