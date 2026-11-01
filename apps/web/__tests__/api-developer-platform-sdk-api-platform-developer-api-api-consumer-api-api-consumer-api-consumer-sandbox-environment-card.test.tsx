import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-sandbox-environment-card";

describe("ConsumerSandboxEnvironmentCard", () => {
  it("shows sandboxes", () => {
    const sandboxes = [{ id: "sb1", name: "Dev Test", status: "active", rps: 10, mockResponses: true, requestCount: 42 }];
    const { container } = render(<Card sandboxes={sandboxes} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Sandbox Environments");
    expect(container.textContent).toContain("Dev Test");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("Mocked");
    expect(container.textContent).toContain("42 requests");
  });
  it("shows empty", () => {
    const { container } = render(<Card sandboxes={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No sandboxes");
  });
});
