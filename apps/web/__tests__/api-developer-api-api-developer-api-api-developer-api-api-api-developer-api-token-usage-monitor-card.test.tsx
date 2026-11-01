import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitorCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-token-usage-monitor-card";

const tokens = [{ token_prefix: "sk-prod-ab", consumer_id: "acme", requests_total: 50000, endpoints_count: 12, error_rate: 0.5 }];

describe("Card", () => {
  it("shows token usage", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitorCard tokens={tokens} highErrorCount={0} appName="App" />);
    expect(container.textContent).toContain("Token Usage");
    expect(container.textContent).toContain("sk-prod-ab");
    expect(container.textContent).toContain("50,000 reqs");
    expect(container.textContent).toContain("12 ep");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitorCard tokens={[]} highErrorCount={0} appName="App" />);
    expect(container.textContent).toContain("No token usage");
  });
});
