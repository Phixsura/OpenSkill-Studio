import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKnativePanel } from "@/components/fleet-knative-panel";
describe("FleetKnativePanel", () => { it("renders", () => {
    const { container } = render(<FleetKnativePanel total={15} ready={15} coldStarts={80} avgLatency={125} />);
    expect(container.textContent).toContain("Knative");
    expect(container.textContent).toContain("80 cold starts");
}); });
