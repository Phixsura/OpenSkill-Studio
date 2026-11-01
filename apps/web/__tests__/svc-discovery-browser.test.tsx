import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SvcDiscoveryBrowser } from "@/components/svc-discovery-browser";

describe("SvcDiscoveryBrowser", () => {
  it("renders services", () => {
    const { container } = render(
      <SvcDiscoveryBrowser total={2} healthy={2} tags={["http", "grpc"]} onDeregister={vi.fn()}
        services={[
          { name: "api", address: "10.0.0.1:8080", tags: ["http", "v2"], status: "healthy" },
          { name: "worker", address: "10.0.0.2:9090", tags: ["grpc"], status: "healthy" },
        ]} />
    );
    expect(container.textContent).toContain("Service Discovery");
    expect(container.textContent).toContain("2/2 healthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("http");
    expect(container.textContent).toContain("worker");
  });
});
