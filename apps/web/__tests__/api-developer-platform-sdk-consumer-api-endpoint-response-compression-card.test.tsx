import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-response-compression-card";

describe("EndpointResponseCompressionCard", () => {
  it("shows configs", () => {
    const configs = [{ path: "/api/users", algorithm: "gzip", minSize: 1024, level: 6, savingsPct: 70, compressedCount: 5000 }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Response Compression");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("gzip");
    expect(container.textContent).toContain("70%");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No compression configured");
  });
});
