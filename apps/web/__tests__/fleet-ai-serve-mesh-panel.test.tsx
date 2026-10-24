import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiServeMeshPanel } from "@/components/fleet-ai-serve-mesh-panel";
describe("FleetAiServeMeshPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiServeMeshPanel nodes={16} healthy={16} rps={800000} p99={30} gpuUtil={85} />);
    expect(container.textContent).toContain("Serving Mesh");
}); });
