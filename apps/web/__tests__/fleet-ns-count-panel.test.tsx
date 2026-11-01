import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNsCountPanel } from "@/components/fleet-ns-count-panel";
describe("FleetNsCountPanel", () => { it("renders", () => {
    const { container } = render(<FleetNsCountPanel total={20} active={12} empty={8} needsCleanup={true} />);
    expect(container.textContent).toContain("Namespaces");
    expect(container.textContent).toContain("Cleanup recommended");
}); });
