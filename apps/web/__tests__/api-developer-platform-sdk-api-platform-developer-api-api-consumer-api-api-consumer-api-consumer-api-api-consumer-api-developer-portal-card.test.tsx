import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-developer-portal-card";

describe("ConsumerApiDeveloperPortalCard", () => {
  it("shows portal", () => {
    const pages = [{ id: "p1", title: "Getting Started", slug: "start", published: true }];
    const features = { changelog: true, status: true, playground: true, sdk: false };
    const { container } = render(<Card title="My API" primaryColor="#3B82F6" pages={pages} features={features} appName="App" />);
    expect(container.textContent).toContain("Developer Portal");
    expect(container.textContent).toContain("My API");
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Live");
    expect(container.textContent).toContain("Playground");
  });
  it("shows empty", () => {
    const { container } = render(<Card title="Portal" primaryColor="#000" pages={[]} features={{ changelog: false, status: false, playground: false, sdk: false }} appName="App" />);
    expect(container.textContent).toContain("No pages");
  });
});
