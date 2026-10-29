import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTrackerCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-consumer-ip-tracker-card";

const records = [{ consumer_id: "acme", unique_ip_count: 15, total_requests: 50000, top_ip: "10.0.0.1" }];

describe("Card", () => {
  it("shows IP data", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTrackerCard records={records} suspiciousCount={1} appName="App" />);
    expect(container.textContent).toContain("Consumer IPs");
    expect(container.textContent).toContain("1 suspicious");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("15 IPs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiConsumerIpTrackerCard records={[]} suspiciousCount={0} appName="App" />);
    expect(container.textContent).toContain("No IP data");
  });
});
