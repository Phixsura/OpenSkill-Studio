import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDnsHealthPanel } from "@/components/fleet-dns-health-panel";
describe("FleetDnsHealthPanel", () => { it("renders", () => {
    const { container } = render(<FleetDnsHealthPanel total={10} healthy={8} failed={2} slow={1} allOk={false} />);
    expect(container.textContent).toContain("DNS Health");
    expect(container.textContent).toContain("2 failed");
}); });
