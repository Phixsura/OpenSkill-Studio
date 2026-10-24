import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudOptPanel } from "@/components/fleet-cloud-opt-panel";
describe("FleetCloudOptPanel", () => { it("renders", () => {
    const { container } = render(<FleetCloudOptPanel totalRecs={10} implemented={7} pending={3} totalSavings={10000} realizedSavings={7000} />);
    expect(container.textContent).toContain("Cloud Optimization");
    expect(container.textContent).toContain("$7,000/mo saved");
}); });
