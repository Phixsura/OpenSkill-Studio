import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataCatPanel } from "@/components/fleet-ai-data-cat-panel";
describe("FleetAiDataCatPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataCatPanel catalogs={2} active={2} datasets={10000} tags={20000} searches={200000} />);
    expect(container.textContent).toContain("Data Catalog");
}); });
