import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRayServePanel } from "@/components/fleet-ray-serve-panel";
describe("FleetRayServePanel", () => { it("renders", () => {
    const { container } = render(<FleetRayServePanel deployments={10} running={10} replicas={50} qps={25000} />);
    expect(container.textContent).toContain("Ray Serve");
}); });
