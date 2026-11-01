import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-error-response-catalog-card";

describe("ErrorResponseCatalogCard", () => {
  it("shows errors", () => {
    const errors = [{ code: "AUTH_001", status: 401, title: "Invalid Token", category: "auth", resolution: "Check your API key" }];
    const { container } = render(<Card errors={errors} appName="App" />);
    expect(container.textContent).toContain("Error Catalog");
    expect(container.textContent).toContain("AUTH_001");
    expect(container.textContent).toContain("401");
    expect(container.textContent).toContain("Invalid Token");
    expect(container.textContent).toContain("Check your API key");
  });
  it("shows empty", () => {
    const { container } = render(<Card errors={[]} appName="App" />);
    expect(container.textContent).toContain("No error codes registered");
  });
});
