import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDnsResolverV9Panel } from "@/components/fleet-dns-resolver-v9-panel";
describe("FleetDnsResolverV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDnsResolverV9Panel zones={50} qps={80000} />);
    expect(container.textContent).toContain("DNS Resolver v9");
}); });
