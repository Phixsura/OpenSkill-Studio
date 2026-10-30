import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-request-validator-card";

describe("ConsumerApiRequestValidatorCard", () => {
  it("shows validations", () => {
    const validations = [{ path: "/api/orders", method: "POST", rules: [{ field: "item_id", type: "required", value: "" }, { field: "qty", type: "min", value: "1" }] }];
    const { container } = render(<Card validations={validations} appName="App" />);
    expect(container.textContent).toContain("Request Validators");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/api/orders");
    expect(container.textContent).toContain("item_id:required");
  });
  it("shows empty", () => {
    const { container } = render(<Card validations={[]} appName="App" />);
    expect(container.textContent).toContain("No validators configured");
  });
});
