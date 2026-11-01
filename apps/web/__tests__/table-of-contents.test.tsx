import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TableOfContents } from "@/components/table-of-contents";

describe("TableOfContents", () => {
  const items = [
    { level: 1, text: "Getting Started", slug: "getting-started" },
    { level: 2, text: "Installation", slug: "installation" },
    { level: 2, text: "Usage", slug: "usage" },
  ];
  it("renders items", () => {
    const { container } = render(<TableOfContents items={items} activeSlug="installation" />);
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("Installation");
    expect(container.textContent).toContain("Usage");
    const links = container.querySelectorAll("a");
    expect(links[0].getAttribute("href")).toBe("#getting-started");
    expect(links.length).toBe(3);
  });
});
