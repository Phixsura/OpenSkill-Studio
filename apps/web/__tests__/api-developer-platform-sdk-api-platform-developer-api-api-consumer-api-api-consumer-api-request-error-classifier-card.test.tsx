import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-error-classifier-card";

describe("RequestErrorClassifierCard", () => {
  it("shows causes", () => {
    const causes = [{ cause: "auth_failure", count: 50 }, { cause: "server_error", count: 10 }];
    const { container } = render(<Card causes={causes} totalErrors={60} appName="App" />);
    expect(container.textContent).toContain("Error Classifier");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("auth_failure");
  });
  it("shows empty", () => {
    const { container } = render(<Card causes={[]} totalErrors={0} appName="App" />);
    expect(container.textContent).toContain("No errors");
  });
});
