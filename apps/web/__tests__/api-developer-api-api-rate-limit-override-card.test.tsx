import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiRateLimitOverrideCard from "../src/components/api-developer-api-api-rate-limit-override-card";

const overrides = [
  { override_id: "o1", consumer_id: "acme-corp", endpoint: "*", limit_per_minute: 5000, reason: "Enterprise", expired: false },
];

describe("APIDeveloperAPIApiRateLimitOverrideCard", () => {
  it("shows overrides", () => {
    const { container } = render(<APIDeveloperAPIApiRateLimitOverrideCard overrides={overrides} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Overrides");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("acme-corp");
    expect(container.textContent).toContain("5,000/min");
    expect(container.textContent).toContain("all endpoints");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiRateLimitOverrideCard overrides={[]} appName="App" />);
    expect(container.textContent).toContain("No overrides");
  });
});
