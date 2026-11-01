import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-payload-size-tracker-card";

describe("RequestPayloadSizeTrackerCard", () => {
  it("shows stats", () => {
    const stats = [{ endpoint: "/users", method: "POST", avg_request_kb: 5, avg_response_kb: 10, total_transfer_mb: 1.5 }];
    const { container } = render(<Card stats={stats} totalTransferMb={1.5} appName="App" />);
    expect(container.textContent).toContain("Payload Sizes");
    expect(container.textContent).toContain("1.5 MB");
    expect(container.textContent).toContain("↑5KB ↓10KB");
  });
  it("shows empty", () => {
    const { container } = render(<Card stats={[]} totalTransferMb={0} appName="App" />);
    expect(container.textContent).toContain("No payload data");
  });
});
