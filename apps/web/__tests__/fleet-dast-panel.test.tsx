import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDastPanel } from "@/components/fleet-dast-panel";
describe("FleetDastPanel", () => { it("renders", () => {
    const { container } = render(<FleetDastPanel scans={5} totalVulns={8} critical={1} secure={false} />);
    expect(container.textContent).toContain("DAST Results");
    expect(container.textContent).toContain("1 critical");
}); });
