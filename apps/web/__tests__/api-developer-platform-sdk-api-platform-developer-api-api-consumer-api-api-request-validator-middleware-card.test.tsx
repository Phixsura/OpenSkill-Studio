import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-validator-middleware-card";

describe("RequestValidatorMiddlewareCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card totalRules={15} rejectionRate={3.5} totalChecked={50000} appName="App" />);
    expect(container.textContent).toContain("Request Validator");
    expect(container.textContent).toContain("15 rules");
    expect(container.textContent).toContain("3.5% rejected");
    expect(container.textContent).toContain("50,000");
  });
  it("shows high rejection", () => {
    const { container } = render(<Card totalRules={5} rejectionRate={25} totalChecked={100} appName="App" />);
    expect(container.textContent).toContain("25% rejected");
  });
});
