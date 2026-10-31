import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDevspacePanel } from "@/components/fleet-devspace-panel";
describe("FleetDevspacePanel", () => { it("renders", () => {
    const { container } = render(<FleetDevspacePanel total={20} active={12} sleeping={8} />);
    expect(container.textContent).toContain("DevSpace");
    expect(container.textContent).toContain("8 sleeping");
}); });
