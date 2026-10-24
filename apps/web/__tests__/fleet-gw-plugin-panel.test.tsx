import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGwPluginPanel } from "@/components/fleet-gw-plugin-panel";
describe("FleetGwPluginPanel", () => { it("renders", () => {
    const { container } = render(<FleetGwPluginPanel total={10} active={8} deprecated={1} healthy={false} />);
    expect(container.textContent).toContain("Gateway Plugins");
    expect(container.textContent).toContain("1 deprecated");
}); });
