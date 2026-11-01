import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTrackerCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-consumer-authentication-tracker-card";

const records = [{ consumer_id: "acme", auth_method: "api_key", successful: 900, failed: 100, failure_rate: 10 }];

describe("Card", () => {
  it("shows auth tracker", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTrackerCard records={records} methodCounts={{ api_key: 3, oauth2: 2 }} highFailureCount={1} appName="App" />);
    expect(container.textContent).toContain("Auth Tracker");
    expect(container.textContent).toContain("1 high failure");
    expect(container.textContent).toContain("api_key: 3");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("10% fail");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiConsumerAuthenticationTrackerCard records={[]} methodCounts={{}} highFailureCount={0} appName="App" />);
    expect(container.textContent).toContain("No auth data");
  });
});
