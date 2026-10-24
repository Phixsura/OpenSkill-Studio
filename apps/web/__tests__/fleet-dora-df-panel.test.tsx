import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDoraDfPanel } from "@/components/fleet-dora-df-panel";
describe("FleetDoraDfPanel", () => { it("renders", () => {
    const { container } = render(<FleetDoraDfPanel deploysPerDay={5} level="Elite" />);
    expect(container.textContent).toContain("DORA: Deploy Freq");
    expect(container.textContent).toContain("Elite");
}); });
