import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNotaryPanel } from "@/components/fleet-notary-panel";
describe("FleetNotaryPanel", () => { it("renders", () => {
    const { container } = render(<FleetNotaryPanel total={50} signed={48} trusted={48} unsigned={2} />);
    expect(container.textContent).toContain("Notary");
    expect(container.textContent).toContain("2 unsigned");
}); });
