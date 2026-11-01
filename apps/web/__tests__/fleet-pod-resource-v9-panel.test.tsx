import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPodResourceV9Panel } from "@/components/fleet-pod-resource-v9-panel";
describe("FleetPodResourceV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPodResourceV9Panel pods={500} cpuUsed={10000} />);
    expect(container.textContent).toContain("Pod Resource v9");
}); });
