import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookContentTypeManagerCard from "../src/components/api-developer-api-webhook-content-type-manager-card";

const configs = [
  { destination: "https://a.com", content_type: "application/json", charset: "utf-8", delivery_count: 100 },
];

describe("APIDeveloperAPIWebhookContentTypeManagerCard", () => {
  it("shows content type configs", () => {
    const { container } = render(<APIDeveloperAPIWebhookContentTypeManagerCard configs={configs} contentTypeBreakdown={{ "application/json": 1 }} appName="App" />);
    expect(container.textContent).toContain("Content Types");
    expect(container.textContent).toContain("json: 1");
    expect(container.textContent).toContain("https://a.com");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookContentTypeManagerCard configs={[]} contentTypeBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No content type configs");
  });
});
