import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceCatalogV9Panel } from "@/components/fleet-service-catalog-v9-panel";
describe("FleetServiceCatalogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceCatalogV9Panel services={300} teams={25} />);
    expect(container.textContent).toContain("Service Catalog v9");
}); });
