import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataCatalogV9Panel } from "@/components/fleet-data-catalog-v9-panel";
describe("FleetDataCatalogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataCatalogV9Panel assets={500} cataloged={500} />);
    expect(container.textContent).toContain("Data Catalog v9");
}); });
