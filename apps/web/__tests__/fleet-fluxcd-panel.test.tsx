import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFluxcdPanel } from "@/components/fleet-fluxcd-panel";
describe("FleetFluxcdPanel", () => { it("renders", () => {
    const { container } = render(<FleetFluxcdPanel total={15} ready={13} notReady={2} suspended={1} allReady={false} />);
    expect(container.textContent).toContain("FluxCD");
    expect(container.textContent).toContain("2 not ready");
}); });
