import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-health-check-config-card";

describe("ConsumerApiHealthCheckConfigCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", interval_s: 30, timeout_ms: 5000, check_path: "/health", healthy_threshold: 2, unhealthy_threshold: 3 }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Health Check Config");
    expect(container.textContent).toContain("/health");
    expect(container.textContent).toContain("30s");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No health check configs");
  });
});
