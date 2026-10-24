import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEnvParityPanel } from "@/components/fleet-env-parity-panel";
describe("FleetEnvParityPanel", () => { it("renders", () => {
    const { container } = render(<FleetEnvParityPanel total={15} matching={13} drifted={2} parity={false} />);
    expect(container.textContent).toContain("Env Parity");
    expect(container.textContent).toContain("2 staging/prod drift");
}); });
