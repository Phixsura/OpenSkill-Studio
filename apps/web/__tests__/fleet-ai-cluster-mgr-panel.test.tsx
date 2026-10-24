import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiClusterMgrPanel } from "@/components/fleet-ai-cluster-mgr-panel";
describe("FleetAiClusterMgrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiClusterMgrPanel managers={5} active={5} clusters={50} nodes={5000} utilization={88} />);
    expect(container.textContent).toContain("Cluster Manager");
}); });
