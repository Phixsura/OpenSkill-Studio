import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLinkerdPanel } from "@/components/fleet-linkerd-panel";
describe("FleetLinkerdPanel", () => { it("renders", () => {
    const { container } = render(<FleetLinkerdPanel total={20} meshed={18} unmeshed={2} avgSuccessRate={99.5} healthy={true} />);
    expect(container.textContent).toContain("Linkerd");
    expect(container.textContent).toContain("99.5%");
}); });
