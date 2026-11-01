import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-key-label-card";

describe("ConsumerApiKeyLabelCard", () => {
  it("shows labels", () => {
    const labels = [{ key_id: "k1", label: "Main Prod Key", environment: "production", tags: ["primary", "ci"] }];
    const { container } = render(<Card labels={labels} appName="App" />);
    expect(container.textContent).toContain("API Key Labels");
    expect(container.textContent).toContain("Main Prod Key");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("ci");
  });
  it("shows empty", () => {
    const { container } = render(<Card labels={[]} appName="App" />);
    expect(container.textContent).toContain("No labeled keys");
  });
});
