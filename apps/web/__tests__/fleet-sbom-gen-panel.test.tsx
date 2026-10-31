import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSbomGenPanel } from "@/components/fleet-sbom-gen-panel";
describe("FleetSbomGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetSbomGenPanel total={100} withSbom={95} coveragePct={95} compliant={true} />);
    expect(container.textContent).toContain("SBOM");
    expect(container.textContent).toContain("95%");
}); });
