import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPixiePanel } from "@/components/fleet-pixie-panel";
describe("FleetPixiePanel", () => { it("renders", () => {
    const { container } = render(<FleetPixiePanel clusters={3} connected={3} monitoredPods={1500} dataGb={150} />);
    expect(container.textContent).toContain("Pixie");
    expect(container.textContent).toContain("1500 pods");
}); });
