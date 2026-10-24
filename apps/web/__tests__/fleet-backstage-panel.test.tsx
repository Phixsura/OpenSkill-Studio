import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBackstagePanel } from "@/components/fleet-backstage-panel";
describe("FleetBackstagePanel", () => { it("renders", () => {
    const { container } = render(<FleetBackstagePanel total={50} registered={40} withTechdocs={30} coveragePct={80} />);
    expect(container.textContent).toContain("Backstage");
    expect(container.textContent).toContain("80%");
}); });
