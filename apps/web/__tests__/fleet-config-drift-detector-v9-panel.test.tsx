import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConfigDriftDetectorV9Panel } from "@/components/fleet-config-drift-detector-v9-panel";
describe("FleetConfigDriftDetectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetConfigDriftDetectorV9Panel configs={100} drifted={0} />);
    expect(container.textContent).toContain("Config Drift Detector v9");
}); });
