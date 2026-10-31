import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-environment-variable-card";

describe("EnvironmentVariableCard", () => {
  it("shows vars", () => {
    const vars = [{ key: "API_URL", value: "https://api.com", secret: false }, { key: "API_KEY", value: "***1234", secret: true }];
    const { container } = render(<Card vars={vars} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Environment Variables");
    expect(container.textContent).toContain("API_URL");
    expect(container.textContent).toContain("***1234");
  });
  it("shows empty", () => {
    const { container } = render(<Card vars={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No environment variables");
  });
});
