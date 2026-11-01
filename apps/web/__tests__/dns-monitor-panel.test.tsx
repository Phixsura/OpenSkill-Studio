import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DnsMonitorPanel } from "@/components/dns-monitor-panel";

describe("DnsMonitorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DnsMonitorPanel healthy={1} total={2} allHealthy={false} results={[
        { domain: "api.example.com", resolved: true, latencyMs: 5, healthy: true },
        { domain: "slow.example.com", resolved: true, latencyMs: 200, healthy: false },
      ]} />
    );
    expect(container.textContent).toContain("DNS Monitor");
    expect(container.textContent).toContain("1/2 healthy");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("5ms");
  });
});
