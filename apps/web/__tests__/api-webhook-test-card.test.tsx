import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookTestCard from "../src/components/api-webhook-test-card";

const results = [
  { test_id: "t1", destination: "https://a.com", status_code: 200, duration_ms: 45, success: true, error: "" },
  { test_id: "t2", destination: "https://b.com", status_code: null, duration_ms: 0, success: false, error: "Refused" },
];

describe("APIWebhookTestCard", () => {
  it("renders header and pass count", () => {
    const { container } = render(<APIWebhookTestCard results={results} appName="App" />);
    expect(container.textContent).toContain("Webhook Tests");
    expect(container.textContent).toContain("1/2 passed");
  });

  it("shows results", () => {
    const { container } = render(<APIWebhookTestCard results={results} appName="App" />);
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("err");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookTestCard results={[]} appName="App" />);
    expect(container.textContent).toContain("No test results");
  });
});
