import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-request-validator-v2-card";

describe("RequestValidatorV2Card", () => {
  it("shows schemas", () => {
    const schemas = [{ id: "s1", endpoint: "/api/orders", method: "POST", rules: [{ field: "data.user.email", type: "required", value: "" }, { field: "quantity", type: "range", value: "1,100" }] }];
    const { container } = render(<Card schemas={schemas} appName="App" />);
    expect(container.textContent).toContain("Request Validator V2");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("data.user.email:required");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} appName="App" />);
    expect(container.textContent).toContain("No validation schemas");
  });
});
