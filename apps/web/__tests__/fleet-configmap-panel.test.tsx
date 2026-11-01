import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetConfigmapPanel } from "@/components/fleet-configmap-panel";
describe("FleetConfigmapPanel", () => { it("renders", () => {
    const { container } = render(<FleetConfigmapPanel total={10} oversized={1} stale={2} clean={false} />);
    expect(container.textContent).toContain("ConfigMaps");
    expect(container.textContent).toContain("1 oversized");
}); });
