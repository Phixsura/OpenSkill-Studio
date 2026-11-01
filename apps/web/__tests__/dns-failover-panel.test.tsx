import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DnsFailoverPanel } from "@/components/dns-failover-panel";

describe("DnsFailoverPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DnsFailoverPanel failedOver={1}
        records={[
          { domain: "api.example.com", primary: "1.1.1.1", secondary: "2.2.2.2", active: "primary", failoverCount: 0 },
          { domain: "web.example.com", primary: "3.3.3.3", secondary: "4.4.4.4", active: "secondary", failoverCount: 2 },
        ]} />
    );
    expect(container.textContent).toContain("DNS Failover");
    expect(container.textContent).toContain("1 failed over");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("web.example.com");
    expect(container.textContent).toContain("secondary");
    expect(container.textContent).toContain("2 failovers");
  });
});
