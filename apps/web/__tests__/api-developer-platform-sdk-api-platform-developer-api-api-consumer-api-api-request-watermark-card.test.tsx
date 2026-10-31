import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-watermark-card";

describe("RequestWatermarkCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card generated={5000} verified={3000} totalWatermarks={5000} appName="App" />);
    expect(container.textContent).toContain("Request Watermarks");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("3,000");
  });
  it("shows zero", () => {
    const { container } = render(<Card generated={0} verified={0} totalWatermarks={0} appName="App" />);
    expect(container.textContent).toContain("Request Watermarks");
  });
});
