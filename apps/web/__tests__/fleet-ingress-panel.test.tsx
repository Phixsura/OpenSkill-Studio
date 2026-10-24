import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIngressPanel } from "@/components/fleet-ingress-panel";
describe("FleetIngressPanel", () => { it("renders", () => {
    const { container } = render(<FleetIngressPanel totalRps={800} routes={10} errorRoutes={1} healthy={false} />);
    expect(container.textContent).toContain("Fleet Ingress");
    expect(container.textContent).toContain("1 high-error");
}); });
