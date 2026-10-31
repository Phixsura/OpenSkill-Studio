import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCrossplanePanel } from "@/components/fleet-crossplane-panel";
describe("FleetCrossplanePanel", () => { it("renders", () => {
    const { container } = render(<FleetCrossplanePanel total={30} ready={28} synced={28} notReady={2} allReady={false} />);
    expect(container.textContent).toContain("Crossplane");
    expect(container.textContent).toContain("2 not ready");
}); });
