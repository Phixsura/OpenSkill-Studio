import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-response-validator-card";

describe("ResponseValidatorCard", () => {
  it("shows expectations", () => {
    const exps = [{ endpoint: "/users", method: "GET", expected_status: 200, field_count: 3 }];
    const { container } = render(<Card expectations={exps} passRate={98.5} appName="App" />);
    expect(container.textContent).toContain("Response Validator");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("GET /users");
  });
  it("shows empty", () => {
    const { container } = render(<Card expectations={[]} passRate={0} appName="App" />);
    expect(container.textContent).toContain("No expectations set");
  });
});
