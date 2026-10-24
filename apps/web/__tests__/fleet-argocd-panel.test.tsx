import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetArgocdPanel } from "@/components/fleet-argocd-panel";
describe("FleetArgocdPanel", () => { it("renders", () => {
    const { container } = render(<FleetArgocdPanel total={20} synced={18} healthy={17} degraded={2} allSynced={false} />);
    expect(container.textContent).toContain("ArgoCD");
    expect(container.textContent).toContain("Out of sync");
}); });
