import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-tenant-config-card";

describe("ConsumerApiTenantConfigCard", () => {
  it("shows config", () => {
    const entries = [{ key: "max_retries", value: "5" }, { key: "debug", value: "true" }];
    const { container } = render(<Card entries={entries} consumerId="c1" version={3} appName="App" />);
    expect(container.textContent).toContain("Tenant Config");
    expect(container.textContent).toContain("max_retries");
    expect(container.textContent).toContain("v3");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} consumerId="c1" version={0} appName="App" />);
    expect(container.textContent).toContain("No config overrides");
  });
});
