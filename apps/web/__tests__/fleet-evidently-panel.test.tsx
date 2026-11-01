import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEvidentlyPanel } from "@/components/fleet-evidently-panel";
describe("FleetEvidentlyPanel", () => { it("renders", () => {
    const { container } = render(<FleetEvidentlyPanel dashboards={10} active={10} reports={500} driftAlerts={5} />);
    expect(container.textContent).toContain("Evidently");
}); });
