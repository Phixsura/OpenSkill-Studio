import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-sdk-config-card";

describe("ConsumerApiSdkConfigCard", () => {
  it("shows configs", () => {
    const configs = [{ id: "c1", language: "typescript", baseUrl: "https://api.ex.com", version: "v2", timeoutMs: 30000, retries: 3 }];
    const { container } = render(<Card configs={configs} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("SDK Configs");
    expect(container.textContent).toContain("TS");
    expect(container.textContent).toContain("https://api.ex.com");
    expect(container.textContent).toContain("3 retries");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No SDK configs");
  });
});
