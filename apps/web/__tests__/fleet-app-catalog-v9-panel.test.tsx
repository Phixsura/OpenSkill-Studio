import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAppCatalogV9Panel } from "@/components/fleet-app-catalog-v9-panel";
describe("FleetAppCatalogV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetAppCatalogV9Panel apps={200} owners={30} />);
    expect(container.textContent).toContain("App Catalog v9");
}); });
