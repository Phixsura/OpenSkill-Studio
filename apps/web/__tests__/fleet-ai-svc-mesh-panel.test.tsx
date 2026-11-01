import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSvcMeshPanel } from "@/components/fleet-ai-svc-mesh-panel";
describe("FleetAiSvcMeshPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSvcMeshPanel meshes={5} active={5} services={200} requests={2000000000} p99={15} />);
    expect(container.textContent).toContain("Service Mesh");
}); });
