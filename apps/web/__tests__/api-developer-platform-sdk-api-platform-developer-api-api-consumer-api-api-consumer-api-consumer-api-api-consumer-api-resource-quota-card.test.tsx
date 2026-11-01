import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-resource-quota-card";

describe("ConsumerApiResourceQuotaCard", () => {
  it("shows quotas", () => {
    const quotas = [{ resource: "webhooks", current: 8, max: 10 }, { resource: "api_keys", current: 2, max: 5 }];
    const { container } = render(<Card quotas={quotas} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Resource Quotas");
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("8/10");
    expect(container.textContent).toContain("2/5");
  });
  it("shows empty", () => {
    const { container } = render(<Card quotas={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No quotas set");
  });
});
