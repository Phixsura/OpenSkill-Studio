import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDashBuildPanel } from "@/components/fleet-ai-dash-build-panel";
describe("FleetAiDashBuildPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDashBuildPanel builders={2} active={2} dashboards={1000} panels={10000} viewers={50000} />);
    expect(container.textContent).toContain("Dashboard Builder");
}); });
