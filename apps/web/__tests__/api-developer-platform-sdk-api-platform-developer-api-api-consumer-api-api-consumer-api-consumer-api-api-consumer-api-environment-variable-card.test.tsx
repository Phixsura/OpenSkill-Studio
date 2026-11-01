import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-environment-variable-card";

describe("ConsumerApiEnvironmentVariableCard", () => {
  it("shows variables", () => {
    const vars = [{ key: "API_URL", value: "https://api.ex.com", sensitive: false, updatedAt: "12:00" }, { key: "SECRET", value: "***", sensitive: true, updatedAt: "12:00" }];
    const { container } = render(<Card variables={vars} environment="production" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Environment Variables");
    expect(container.textContent).toContain("API_URL");
    expect(container.textContent).toContain("production");
  });
  it("shows empty", () => {
    const { container } = render(<Card variables={[]} environment="staging" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No variables");
  });
});
