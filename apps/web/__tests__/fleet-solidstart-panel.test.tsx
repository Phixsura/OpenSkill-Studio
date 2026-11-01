import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSolidstartPanel } from "@/components/fleet-solidstart-panel";
describe("FleetSolidstartPanel", () => { it("renders", () => {
    const { container } = render(<FleetSolidstartPanel apps={5} running={5} routes={100} signals={500} />);
    expect(container.textContent).toContain("SolidStart");
    expect(container.textContent).toContain("500 signals");
}); });
