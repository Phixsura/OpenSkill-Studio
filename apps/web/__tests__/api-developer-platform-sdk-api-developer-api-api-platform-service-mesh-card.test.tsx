import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMeshCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-service-mesh-card";

const routes = [{ source: "api-gateway", destination: "user-service", protocol: "grpc", request_count: 50000, error_rate: 0.5, latency_ms: 15 }];

describe("Card", () => {
  it("shows service mesh", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMeshCard routes={routes} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("api-gateway");
    expect(container.textContent).toContain("user-service");
    expect(container.textContent).toContain("grpc");
    expect(container.textContent).toContain("0.5% err");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformServiceMeshCard routes={[]} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No service routes");
  });
});
