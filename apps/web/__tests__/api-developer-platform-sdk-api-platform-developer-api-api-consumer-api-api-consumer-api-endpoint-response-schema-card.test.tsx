import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-response-schema-card";

describe("EndpointResponseSchemaCard", () => {
  it("shows schemas", () => {
    const schemas = [{ endpoint: "/users", method: "GET", status_code: 200, field_count: 5, required_count: 3 }];
    const { container } = render(<Card schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Response Schemas");
    expect(container.textContent).toContain("GET /users → 200");
    expect(container.textContent).toContain("3/5 req");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No response schemas");
  });
});
