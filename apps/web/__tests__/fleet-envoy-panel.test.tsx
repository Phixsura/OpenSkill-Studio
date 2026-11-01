import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEnvoyPanel } from "@/components/fleet-envoy-panel";
describe("FleetEnvoyPanel", () => { it("renders", () => {
    const { container } = render(<FleetEnvoyPanel total={50} live={49} draining={1} totalRps={100000} />);
    expect(container.textContent).toContain("Envoy");
    expect(container.textContent).toContain("100,000 rps");
}); });
