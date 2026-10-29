import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookContentTypeCard from "../src/components/api-webhook-content-type-card";

const configs = [
  { destination: "https://xml-api.com", content_type: "application/xml", delivery_count: 50 },
];

describe("APIWebhookContentTypeCard", () => {
  it("renders header and default", () => {
    const { container } = render(<APIWebhookContentTypeCard configs={configs} defaultType="application/json" appName="App" />);
    expect(container.textContent).toContain("Content Types");
    expect(container.textContent).toContain("default: application/json");
  });

  it("shows overrides", () => {
    const { container } = render(<APIWebhookContentTypeCard configs={configs} defaultType="application/json" appName="App" />);
    expect(container.textContent).toContain("xml-api.com");
    expect(container.textContent).toContain("application/xml");
  });

  it("shows all-default state", () => {
    const { container } = render(<APIWebhookContentTypeCard configs={[]} defaultType="application/json" appName="App" />);
    expect(container.textContent).toContain("All using default");
  });
});
