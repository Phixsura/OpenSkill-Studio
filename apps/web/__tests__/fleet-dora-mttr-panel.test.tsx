import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDoraMttrPanel } from "@/components/fleet-dora-mttr-panel";
describe("FleetDoraMttrPanel", () => { it("renders", () => {
    const { container } = render(<FleetDoraMttrPanel mttrHours={0.5} level="Elite" />);
    expect(container.textContent).toContain("DORA: MTTR");
    expect(container.textContent).toContain("Elite");
}); });
