import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDnsPanel } from "@/components/fleet-ai-dns-panel";
describe("FleetAiDnsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDnsPanel resolvers={4} active={4} queries={500000000} cacheHit={97} services={1000} />);
    expect(container.textContent).toContain("DNS Resolver");
}); });
