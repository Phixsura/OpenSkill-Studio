import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCatMaturityPanel } from "@/components/fleet-cat-maturity-panel";
describe("FleetCatMaturityPanel", () => { it("renders", () => {
    const { container } = render(<FleetCatMaturityPanel total={30} fullyCataloged={25} partial={5} maturityPct={83.3} mature={true} />);
    expect(container.textContent).toContain("Catalog Maturity");
    expect(container.textContent).toContain("83.3%");
}); });
