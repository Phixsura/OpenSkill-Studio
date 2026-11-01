import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-documentation-card";

describe("ConsumerApiDocumentationCard", () => {
  it("shows pages", () => {
    const pages = [{ id: "p1", title: "Getting Started", category: "guide", published: true, updatedAt: "2026-06-01" }];
    const { container } = render(<Card pages={pages} appName="App" />);
    expect(container.textContent).toContain("API Documentation");
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("guide");
    expect(container.textContent).toContain("Published");
  });
  it("shows empty", () => {
    const { container } = render(<Card pages={[]} appName="App" />);
    expect(container.textContent).toContain("No documentation");
  });
});
