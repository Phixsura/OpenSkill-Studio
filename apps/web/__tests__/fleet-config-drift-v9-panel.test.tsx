import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConfigDriftV9Panel } from "@/components/fleet-config-drift-v9-panel";
describe("FleetConfigDriftV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetConfigDriftV9Panel total={100} drifted={0} />);
    expect(container.textContent).toContain("Config Drift v9");
}); });
