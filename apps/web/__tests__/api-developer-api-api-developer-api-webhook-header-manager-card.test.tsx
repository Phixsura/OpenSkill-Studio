import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiWebhookHeaderManagerCard from "../src/components/api-developer-api-api-developer-api-webhook-header-manager-card";

const configs = [{ destination: "https://api.example.com/hook", headers: { "X-Custom": "value", "X-Source": "platform" } }];

describe("APIDeveloperAPIApiDeveloperApiWebhookHeaderManagerCard", () => {
  it("shows headers", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiWebhookHeaderManagerCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Custom Headers");
    expect(container.textContent).toContain("2 headers");
    expect(container.textContent).toContain("X-Custom: value");
    expect(container.textContent).toContain("X-Source: platform");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiWebhookHeaderManagerCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No custom headers");
  });
});
