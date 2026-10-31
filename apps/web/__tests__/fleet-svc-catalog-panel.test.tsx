import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSvcCatalogPanel } from "@/components/fleet-svc-catalog-panel";
describe("FleetSvcCatalogPanel", () => { it("renders", () => {
    const { container } = render(<FleetSvcCatalogPanel total={20} withOwner={18} withDocs={15} withRunbook={10} completenessPct={71.7} />);
    expect(container.textContent).toContain("Service Catalog");
    expect(container.textContent).toContain("71.7% complete");
}); });
