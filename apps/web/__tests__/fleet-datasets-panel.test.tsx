import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDatasetsPanel } from "@/components/fleet-datasets-panel";
describe("FleetDatasetsPanel", () => { it("renders", () => {
    const { container } = render(<FleetDatasetsPanel repos={10} active={10} datasets={1000} totalRows={500000000} />);
    expect(container.textContent).toContain("Datasets");
}); });
