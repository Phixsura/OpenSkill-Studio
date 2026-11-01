import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodRestartPanel } from "@/components/fleet-pod-restart-panel";
describe("FleetPodRestartPanel", () => { it("renders", () => {
    const { container } = render(<FleetPodRestartPanel totalRestarts={9} crashlooping={1} pods={3} stable={false} />);
    expect(container.textContent).toContain("Pod Restarts");
    expect(container.textContent).toContain("1 crashlooping");
}); });
