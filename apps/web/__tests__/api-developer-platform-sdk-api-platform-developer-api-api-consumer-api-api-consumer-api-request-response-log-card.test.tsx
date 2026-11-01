import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-response-log-card";

describe("RequestResponseLogCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card entryCount={50000} avgDuration={45} totalBandwidthMb={256} appName="App" />);
    expect(container.textContent).toContain("Request/Response Log");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("256 MB");
  });
  it("shows zero", () => {
    const { container } = render(<Card entryCount={0} avgDuration={0} totalBandwidthMb={0} appName="App" />);
    expect(container.textContent).toContain("Request/Response Log");
  });
});
