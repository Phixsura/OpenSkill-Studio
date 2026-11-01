import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-timeout-policy-card";

describe("TimeoutPolicyCard", () => {
  it("shows policies", () => {
    const policies = [{ endpoint: "/slow", method: "GET", timeout_ms: 60000, retry_on_timeout: true, max_retries: 2 }];
    const { container } = render(<Card policies={policies} defaultTimeout={30000} timeoutCount={5} appName="App" />);
    expect(container.textContent).toContain("Timeout Policies");
    expect(container.textContent).toContain("60000ms");
    expect(container.textContent).toContain("5 timeouts");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} defaultTimeout={30000} timeoutCount={0} appName="App" />);
    expect(container.textContent).toContain("No custom timeout policies");
  });
});
