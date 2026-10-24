import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArgoRollPanel } from "@/components/fleet-argo-roll-panel";
describe("FleetArgoRollPanel", () => { it("renders", () => {
    const { container } = render(<FleetArgoRollPanel total={10} healthy={8} paused={1} degraded={1} />);
    expect(container.textContent).toContain("Argo Rollouts");
}); });
