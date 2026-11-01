import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-consumer-api-consumer-api-api-consumer-request-size-analyzer-card";

describe("RequestSizeAnalyzerCard", () => {
  it("shows analyses", () => {
    const analyses = [{ endpoint: "/api/users", samples: 1000, avgReqBytes: 256, avgRespBytes: 5120, maxReqBytes: 1024, maxRespBytes: 51200 }];
    const { container } = render(<Card analyses={analyses} totalTransferGb={1.5} largestEndpoint="/api/users" appName="App" />);
    expect(container.textContent).toContain("Request Size Analyzer");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("5.0 KB");
    expect(container.textContent).toContain("1.5 GB");
  });
  it("shows empty", () => {
    const { container } = render(<Card analyses={[]} totalTransferGb={0} largestEndpoint="" appName="App" />);
    expect(container.textContent).toContain("No size data");
  });
});
