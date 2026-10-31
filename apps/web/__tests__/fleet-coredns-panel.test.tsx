import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCorednsPanel } from "@/components/fleet-coredns-panel";
describe("FleetCorednsPanel", () => { it("renders", () => {
    const { container } = render(<FleetCorednsPanel instances={3} healthy={3} qps={30000} cacheHitPct={90} />);
    expect(container.textContent).toContain("CoreDNS");
    expect(container.textContent).toContain("30,000 qps");
}); });
