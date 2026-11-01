import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInfraDriftPanel } from "@/components/fleet-infra-drift-panel";
describe("FleetInfraDriftPanel", () => { it("renders", () => {
    const { container } = render(<FleetInfraDriftPanel total={100} drifted={3} unmanaged={2} clean={false} />);
    expect(container.textContent).toContain("IaC Drift");
    expect(container.textContent).toContain("3 drifted");
}); });
