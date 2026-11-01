import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-sdk-code-sample-card";

describe("SdkCodeSampleCard", () => {
  it("shows samples", () => {
    const samples = [{ sample_id: "s1", endpoint: "/users", method: "GET", language: "python" }];
    const { container } = render(<Card samples={samples} totalSamples={5} languages={["python", "curl"]} appName="App" />);
    expect(container.textContent).toContain("Code Samples");
    expect(container.textContent).toContain("5 samples");
    expect(container.textContent).toContain("python");
    expect(container.textContent).toContain("GET /users");
  });
  it("shows empty", () => {
    const { container } = render(<Card samples={[]} totalSamples={0} languages={[]} appName="App" />);
    expect(container.textContent).toContain("No code samples");
  });
});
