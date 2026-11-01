import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-id-generator-card";

describe("RequestIdGeneratorCard", () => {
  it("shows config", () => {
    const { container } = render(<Card totalGenerated={50000} format="hex" prefix="req" appName="App" />);
    expect(container.textContent).toContain("Request ID Generator");
    expect(container.textContent).toContain("50,000 generated");
    expect(container.textContent).toContain("req-*");
    expect(container.textContent).toContain("hex");
  });
  it("shows zero", () => {
    const { container } = render(<Card totalGenerated={0} format="uuid" prefix="api" appName="App" />);
    expect(container.textContent).toContain("api-*");
  });
});
