import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiWebhookTestingSandboxCard from "../src/components/api-developer-api-api-developer-api-webhook-testing-sandbox-card";

const tests = [
  { test_id: "t1", destination: "https://a.com", event_type: "push", status_code: 200, duration_ms: 50, success: true },
  { test_id: "t2", destination: "https://a.com", event_type: "issue", status_code: 500, duration_ms: 120, success: false },
];

describe("APIDeveloperAPIApiDeveloperApiWebhookTestingSandboxCard", () => {
  it("shows test results", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiWebhookTestingSandboxCard tests={tests} successRate={66.7} appName="App" />);
    expect(container.textContent).toContain("Webhook Sandbox");
    expect(container.textContent).toContain("66.7%");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiWebhookTestingSandboxCard tests={[]} successRate={0} appName="App" />);
    expect(container.textContent).toContain("No test deliveries");
  });
});
