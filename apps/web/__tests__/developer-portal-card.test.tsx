import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeveloperPortalCard from "../src/components/developer-portal-card";

const sections = [
  {
    section_id: "s1",
    title: "Getting Started",
    items: [
      { label: "Quickstart", href: "/quickstart" },
      { label: "Auth", href: "/auth" },
    ],
  },
  { section_id: "s2", title: "API Reference", items: [{ label: "REST API", href: "/api" }] },
];

describe("DeveloperPortalCard", () => {
  it("renders portal name and welcome", () => {
    const { container } = render(
      <DeveloperPortalCard
        portalName="My Portal"
        themeColor="#3B82F6"
        welcomeMessage="Welcome devs!"
        sections={sections}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("My Portal");
    expect(container.textContent).toContain("Welcome devs!");
  });

  it("shows section count", () => {
    const { container } = render(
      <DeveloperPortalCard
        portalName="P"
        themeColor="#000"
        welcomeMessage=""
        sections={sections}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("2 sections");
  });

  it("shows section titles and items", () => {
    const { container } = render(
      <DeveloperPortalCard
        portalName="P"
        themeColor="#000"
        welcomeMessage=""
        sections={sections}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Quickstart");
    expect(container.textContent).toContain("REST API");
  });

  it("shows empty state", () => {
    const { container } = render(
      <DeveloperPortalCard
        portalName="P"
        themeColor="#000"
        welcomeMessage=""
        sections={[]}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("No navigation sections");
  });
});
