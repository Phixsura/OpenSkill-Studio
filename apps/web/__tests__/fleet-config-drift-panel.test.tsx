import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConfigDriftPanel } from "@/components/fleet-config-drift-panel";
describe("FleetConfigDriftPanel", () => { it("renders", () => {
    const { container } = render(<FleetConfigDriftPanel drifted={1} total={5} consistent={false} />);
    expect(container.textContent).toContain("Config Drift");
    expect(container.textContent).toContain("1/5 drifted");
}); });
