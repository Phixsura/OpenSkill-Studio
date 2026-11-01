import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSidecarPanel } from "@/components/fleet-sidecar-panel";
describe("FleetSidecarPanel", () => { it("renders", () => {
    const { container } = render(<FleetSidecarPanel total={10} injected={8} missing={2} coveragePct={80} />);
    expect(container.textContent).toContain("Sidecar Injection");
    expect(container.textContent).toContain("2 without");
}); });
