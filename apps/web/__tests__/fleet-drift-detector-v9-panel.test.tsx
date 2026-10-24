import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDriftDetectorV9Panel } from "@/components/fleet-drift-detector-v9-panel";
describe("FleetDriftDetectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDriftDetectorV9Panel resources={200} drifted={0} />);
    expect(container.textContent).toContain("Drift Detector v9");
}); });
