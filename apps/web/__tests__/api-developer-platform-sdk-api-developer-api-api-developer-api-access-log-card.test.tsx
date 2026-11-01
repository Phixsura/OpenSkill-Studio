import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLogCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-developer-api-access-log-card";

const entries = [
  { entry_id: "e1", consumer_id: "acme", method: "GET", path: "/api/users", status_code: 200, latency_ms: 45 },
  { entry_id: "e2", consumer_id: "acme", method: "POST", path: "/api/orders", status_code: 500, latency_ms: 120 },
];

describe("Card", () => {
  it("shows access log", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLogCard entries={entries} totalCount={50000} errorCount={150} appName="App" />);
    expect(container.textContent).toContain("Access Log");
    expect(container.textContent).toContain("50,000 entries");
    expect(container.textContent).toContain("150 errors");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperApiAccessLogCard entries={[]} totalCount={0} errorCount={0} appName="App" />);
    expect(container.textContent).toContain("No access logs");
  });
});
