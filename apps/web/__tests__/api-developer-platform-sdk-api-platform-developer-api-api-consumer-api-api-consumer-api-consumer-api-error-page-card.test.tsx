import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-error-page-card";

describe("ConsumerApiErrorPageCard", () => {
  it("shows templates", () => {
    const templates = [{ statusCode: 404, errorCode: "NOT_FOUND", title: "Not Found", docsUrl: "https://docs.ex.com", hasOverride: true }];
    const { container } = render(<Card templates={templates} appName="App" />);
    expect(container.textContent).toContain("Error Pages");
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("Not Found");
    expect(container.textContent).toContain("NOT_FOUND");
    expect(container.textContent).toContain("custom");
  });
  it("shows default", () => {
    const { container } = render(<Card templates={[]} appName="App" />);
    expect(container.textContent).toContain("Using default errors");
  });
});
