import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIstioPanel } from "@/components/fleet-istio-panel";
describe("FleetIstioPanel", () => { it("renders", () => {
    const { container } = render(<FleetIstioPanel total={50} synced={48} outOfSync={2} versionMismatch={1} healthy={false} />);
    expect(container.textContent).toContain("Istio");
    expect(container.textContent).toContain("2 out of sync");
}); });
