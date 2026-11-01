import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcDiscoveryPanel } from "@/components/svc-discovery-panel";

describe("SvcDiscoveryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SvcDiscoveryPanel healthy={3} stale={1}
        services={[
          { name: "api", endpoint: "10.0.0.1:8080", tags: ["http", "rest"] },
          { name: "worker", endpoint: "10.0.0.2:9090", tags: ["grpc"] },
        ]} />
    );
    expect(container.textContent).toContain("Service Discovery");
    expect(container.textContent).toContain("3 healthy");
    expect(container.textContent).toContain("1 stale");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("http");
    expect(container.textContent).toContain("grpc");
  });
});
