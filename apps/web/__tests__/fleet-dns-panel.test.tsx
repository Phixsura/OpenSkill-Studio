import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDnsPanel } from "@/components/fleet-dns-panel";
describe("FleetDnsPanel", () => { it("renders", () => {
    const { container } = render(<FleetDnsPanel avgMs={15} failures={0} healthy={true} />);
    expect(container.textContent).toContain("Fleet DNS");
    expect(container.textContent).toContain("Healthy");
}); });
