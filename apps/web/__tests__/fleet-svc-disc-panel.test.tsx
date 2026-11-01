import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSvcDiscPanel } from "@/components/fleet-svc-disc-panel";
describe("FleetSvcDiscPanel", () => { it("renders", () => {
    const { container } = render(<FleetSvcDiscPanel total={20} resolvable={19} staleDns={1} healthy={false} />);
    expect(container.textContent).toContain("Service Discovery");
    expect(container.textContent).toContain("1 stale");
}); });
