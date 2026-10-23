import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BlogPostCard } from "@/components/blog-post-card";

describe("BlogPostCard", () => {
  it("renders", () => {
    const { container } = render(
      <BlogPostCard title="Getting Started with Webhooks" excerpt="Learn how to set up webhooks"
        category="tutorial" date="Oct 23, 2026" readTime={5} slug="webhooks-guide" author="Alice" />
    );
    expect(container.textContent).toContain("Getting Started with Webhooks");
    expect(container.textContent).toContain("tutorial");
    expect(container.textContent).toContain("5 min read");
    expect(container.textContent).toContain("By Alice");
    expect(container.querySelector("a")?.getAttribute("href")).toBe("/blog/webhooks-guide");
  });
});
