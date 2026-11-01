import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-response-envelope-card";

describe("ResponseEnvelopeCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", wrap_key: "results", include_meta: true, include_pagination: true }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Response Envelope");
    expect(container.textContent).toContain("results");
    expect(container.textContent).toContain("+meta");
    expect(container.textContent).toContain("+page");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No envelope configs");
  });
});
