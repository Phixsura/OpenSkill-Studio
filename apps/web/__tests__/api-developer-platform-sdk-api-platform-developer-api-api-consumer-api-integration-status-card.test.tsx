import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-integration-status-card";

describe("IntegrationStatusCard", () => {
  it("shows status", () => {
    const checks = [{ check_id: "c1", name: "API key", passed: true, required: true }, { check_id: "c2", name: "Webhook", passed: false, required: false }];
    const { container } = render(<Card consumerId="c1" phase="in_progress" checks={checks} completionPct={50} readyForProd={false} appName="App" />);
    expect(container.textContent).toContain("Integration Status");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("API key");
    expect(container.textContent).toContain("(optional)");
  });
  it("shows ready", () => {
    const { container } = render(<Card consumerId="c1" phase="production" checks={[]} completionPct={100} readyForProd={true} appName="App" />);
    expect(container.textContent).toContain("Ready");
  });
});
