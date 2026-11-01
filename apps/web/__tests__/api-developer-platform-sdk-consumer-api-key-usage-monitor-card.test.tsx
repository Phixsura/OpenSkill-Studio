import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-key-usage-monitor-card";

describe("ApiKeyUsageMonitorCard", () => {
  it("shows snapshots", () => {
    const snapshots = [{ keyId: "k1", reqsLastMin: 15, reqsLastHour: 500, errorsLastHour: 3, avgMs: 75, status: "active" }];
    const { container } = render(<Card snapshots={snapshots} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Key Usage Monitor");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("15/min");
    expect(container.textContent).toContain("3 err");
  });
  it("shows empty", () => {
    const { container } = render(<Card snapshots={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No key usage data");
  });
});
