import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDnsFailoverV9Panel } from "@/components/fleet-dns-failover-v9-panel";
describe("FleetDnsFailoverV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDnsFailoverV9Panel records={10} passing={10} />);
    expect(container.textContent).toContain("DNS Failover v9");
}); });
