import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMeshTimeoutPanel } from "@/components/fleet-mesh-timeout-panel";
describe("FleetMeshTimeoutPanel", () => { it("renders", () => {
    const { container } = render(<FleetMeshTimeoutPanel requests={10000} timeouts={150} timeoutRate={1.5} problematic={true} />);
    expect(container.textContent).toContain("Mesh Timeouts");
    expect(container.textContent).toContain("High timeout rate");
}); });
