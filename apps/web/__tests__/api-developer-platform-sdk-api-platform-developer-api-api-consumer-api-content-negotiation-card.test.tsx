import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-content-negotiation-card";

describe("ContentNegotiationCard", () => {
  it("shows preferences", () => {
    const prefs = [{ consumer_id: "c1", preferred_format: "xml", accepted_formats: ["xml", "json"], compression: "gzip" }];
    const { container } = render(<Card preferences={prefs} appName="App" />);
    expect(container.textContent).toContain("Content Negotiation");
    expect(container.textContent).toContain("xml");
    expect(container.textContent).toContain("gzip");
  });
  it("shows empty", () => {
    const { container } = render(<Card preferences={[]} appName="App" />);
    expect(container.textContent).toContain("No preferences set");
  });
});
