import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKubesharkPanel } from "@/components/fleet-kubeshark-panel";
describe("FleetKubesharkPanel", () => { it("renders", () => {
    const { container } = render(<FleetKubesharkPanel total={5} active={3} requestsCaptured={100000} anomalies={5} />);
    expect(container.textContent).toContain("Kubeshark");
    expect(container.textContent).toContain("5 anomalies");
}); });
