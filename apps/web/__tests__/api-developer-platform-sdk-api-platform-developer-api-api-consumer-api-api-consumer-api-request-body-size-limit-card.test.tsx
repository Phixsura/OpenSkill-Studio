import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-body-size-limit-card";

describe("RequestBodySizeLimitCard", () => {
  it("shows limits", () => {
    const limits = [{ endpoint: "/api", method: "POST", max_kb: 1, rejection_rate: 5, rejected_count: 50 }];
    const { container } = render(<Card limits={limits} defaultMaxKb={1024} appName="App" />);
    expect(container.textContent).toContain("Body Size Limits");
    expect(container.textContent).toContain("1KB");
    expect(container.textContent).toContain("5% rejected");
  });
  it("shows empty", () => {
    const { container } = render(<Card limits={[]} defaultMaxKb={1024} appName="App" />);
    expect(container.textContent).toContain("No custom limits");
  });
});
