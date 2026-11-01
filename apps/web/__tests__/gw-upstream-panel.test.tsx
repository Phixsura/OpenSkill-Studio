import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwUpstreamPanel } from "@/components/gw-upstream-panel";
describe("GwUpstreamPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwUpstreamPanel healthy={1} unhealthy={1}
        upstreams={[
          { name: "api-1", address: "10.0.0.1:8080", successRate: 99, avgMs: 50, healthy: true },
          { name: "api-2", address: "10.0.0.2:8080", successRate: 50, avgMs: 500, healthy: false },
        ]} />
    );
    expect(container.textContent).toContain("Gateway Upstreams");
    expect(container.textContent).toContain("1 healthy");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("api-1");
    expect(container.textContent).toContain("99%");
    expect(container.textContent).toContain("api-2");
  });
});
