import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodDisruptionV9Panel } from "@/components/fleet-pod-disruption-v9-panel";
describe("FleetPodDisruptionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPodDisruptionV9Panel pdbs={15} disruptions={0} />);
    expect(container.textContent).toContain("Pod Disruption v9");
}); });
