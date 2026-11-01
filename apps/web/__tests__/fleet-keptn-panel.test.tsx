import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKeptnPanel } from "@/components/fleet-keptn-panel";
describe("FleetKeptnPanel", () => { it("renders", () => {
    const { container } = render(<FleetKeptnPanel total={10} deployed={8} evaluating={1} failed={1} />);
    expect(container.textContent).toContain("Keptn");
    expect(container.textContent).toContain("8 deployed");
}); });
