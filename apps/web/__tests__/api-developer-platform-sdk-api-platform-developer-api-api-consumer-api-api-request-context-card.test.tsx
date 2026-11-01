import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-context-card";

describe("RequestContextCard", () => {
  it("shows contexts", () => {
    const regions = [{ region: "us-east", count: 50 }, { region: "eu-west", count: 30 }];
    const { container } = render(<Card activeContexts={80} regions={regions} appName="App" />);
    expect(container.textContent).toContain("Request Context");
    expect(container.textContent).toContain("80");
    expect(container.textContent).toContain("us-east");
    expect(container.textContent).toContain("50");
  });
  it("shows empty regions", () => {
    const { container } = render(<Card activeContexts={0} regions={[]} appName="App" />);
    expect(container.textContent).toContain("Request Context");
  });
});
