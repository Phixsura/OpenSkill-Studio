import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDocumentationCard from "../src/components/api-documentation-card";

const pages = [
  { page_id: "p1", title: "Getting Started", section: "guides", view_count: 500 },
  { page_id: "p2", title: "Authentication", section: "auth", view_count: 300 },
];

describe("APIDocumentationCard", () => {
  it("renders header and stats", () => {
    const { container } = render(
      <APIDocumentationCard pages={pages} sections={["guides", "auth"]} appName="App" />,
    );
    expect(container.textContent).toContain("API Documentation");
    expect(container.textContent).toContain("2 pages");
    expect(container.textContent).toContain("800 views");
  });

  it("shows section chips", () => {
    const { container } = render(
      <APIDocumentationCard pages={pages} sections={["guides", "auth"]} appName="App" />,
    );
    expect(container.textContent).toContain("guides");
    expect(container.textContent).toContain("auth");
  });

  it("shows page titles and views", () => {
    const { container } = render(
      <APIDocumentationCard pages={pages} sections={[]} appName="App" />,
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("500 views");
  });

  it("shows empty state", () => {
    const { container } = render(<APIDocumentationCard pages={[]} sections={[]} appName="App" />);
    expect(container.textContent).toContain("No documentation pages");
  });
});
