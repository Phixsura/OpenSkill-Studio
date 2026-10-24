import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMulticlusterPanel } from "@/components/fleet-multicluster-panel";
describe("FleetMulticlusterPanel", () => { it("renders", () => {
    const { container } = render(<FleetMulticlusterPanel total={3} healthy={2} degraded={1} down={0} allOk={false} />);
    expect(container.textContent).toContain("Multi-Cluster");
}); });
