import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIConsumerHealthCard from "../src/components/api-developer-api-consumer-health-card";
const consumers = [{ consumer_id: "app-1", status: "healthy", error_rate: 1, total_requests: 5000 }, { consumer_id: "app-2", status: "degraded", error_rate: 15, total_requests: 100 }];
describe("APIDeveloperAPIConsumerHealthCard", () => {
  it("shows health", () => {
    const { container } = render(<APIDeveloperAPIConsumerHealthCard consumers={consumers} appName="App" />);
    expect(container.textContent).toContain("Consumer Health");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("app-1");
  });
});
