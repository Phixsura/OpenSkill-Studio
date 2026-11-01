import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-correlation-id-card";

describe("RequestCorrelationIdCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card totalCorrelations={50000} avgChainDepth={3} appName="App" />);
    expect(container.textContent).toContain("Correlation IDs");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("3");
  });
  it("shows zero", () => {
    const { container } = render(<Card totalCorrelations={0} avgChainDepth={0} appName="App" />);
    expect(container.textContent).toContain("Correlation IDs");
  });
});
