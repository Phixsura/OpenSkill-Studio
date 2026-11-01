import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDnsSecurityV9Panel } from "@/components/fleet-dns-security-v9-panel";
describe("FleetDnsSecurityV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDnsSecurityV9Panel zones={20} dnssec={20} />);
    expect(container.textContent).toContain("DNS Security v9");
}); });
