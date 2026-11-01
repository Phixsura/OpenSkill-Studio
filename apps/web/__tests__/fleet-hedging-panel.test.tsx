import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHedgingPanel } from "@/components/fleet-hedging-panel";
describe("FleetHedgingPanel", () => { it("renders", () => {
    const { container } = render(<FleetHedgingPanel totalHedged={1000} saved={200} effectivenessPct={20} worthwhile={true} />);
    expect(container.textContent).toContain("Request Hedging");
    expect(container.textContent).toContain("Effective");
}); });
