import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealthCard from "../src/components/api-developer-api-api-developer-api-api-webhook-destination-health-card";

const destinations = [
  { destination: "https://api.example.com/hook", success_rate: 99.5, avg_response_ms: 45, status: "healthy", total_deliveries: 5000, consecutive_failures: 0 },
  { destination: "https://slow.example.com/hook", success_rate: 75, avg_response_ms: 2000, status: "down", total_deliveries: 100, consecutive_failures: 15 },
];

describe("APIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealthCard", () => {
  it("shows destinations", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealthCard destinations={destinations} unhealthyCount={1} appName="App" />);
    expect(container.textContent).toContain("Destination Health");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("2000ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealthCard destinations={[]} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No destinations");
  });
});
