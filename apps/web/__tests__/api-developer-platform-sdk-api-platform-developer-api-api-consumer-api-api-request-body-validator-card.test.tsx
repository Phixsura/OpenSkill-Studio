import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-body-validator-card";

describe("RequestBodyValidatorCard", () => {
  it("shows schemas", () => {
    const schemas = [{ endpoint: "/users", method: "POST", required_count: 3, typed_count: 5 }];
    const { container } = render(<Card schemas={schemas} validationRate={98.5} appName="App" />);
    expect(container.textContent).toContain("Body Validator");
    expect(container.textContent).toContain("POST /users");
    expect(container.textContent).toContain("98.5%");
  });
  it("shows empty", () => {
    const { container } = render(<Card schemas={[]} validationRate={0} appName="App" />);
    expect(container.textContent).toContain("No body schemas");
  });
});
