import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataLocPanel } from "@/components/fleet-data-loc-panel";
describe("FleetDataLocPanel", () => { it("renders", () => {
    const { container } = render(<FleetDataLocPanel total={10} compliant={9} violations={1} fullyCompliant={false} />);
    expect(container.textContent).toContain("Data Locality");
    expect(container.textContent).toContain("1 residency");
}); });
