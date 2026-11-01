import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatKpiPanel } from "@/components/fleet-ai-plat-kpi-panel";
describe("FleetAiPlatKpiPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatKpiPanel dashboards={3} active={3} kpis={100} green={98} red={2} />);
    expect(container.textContent).toContain("Platform KPI");
}); });
