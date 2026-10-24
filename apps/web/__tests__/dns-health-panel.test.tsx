import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DnsHealthPanel } from "@/components/dns-health-panel";

describe("DnsHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DnsHealthPanel healthy={1} unhealthy={1} allHealthy={false}
        records={[
          { domain: "api.example.com", type: "A", resolved: true, ttl: 300, ip: "1.2.3.4" },
          { domain: "bad.example.com", type: "A", resolved: false, ttl: 0, ip: "" },
        ]} />
    );
    expect(container.textContent).toContain("DNS Health");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("1.2.3.4");
    expect(container.textContent).toContain("unresolved");
  });
});
