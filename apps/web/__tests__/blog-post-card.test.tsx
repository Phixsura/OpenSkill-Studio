import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BlogPostCard } from "@/components/blog-post-card";

describe("BlogPostCard", () => {
  it("renders post", () => {
    const onClick = vi.fn();
    const { container, getByText } = render(
      <BlogPostCard slug="sso" title="SSO is here!" excerpt="Enterprise auth"
        author="Team" date="2026-10-24" readTime="3 min" tags={["sso"]}
        featured={true} onClick={onClick} />
    );
    expect(container.textContent).toContain("SSO is here!");
    expect(container.textContent).toContain("Featured");
    expect(container.textContent).toContain("Enterprise auth");
    expect(container.textContent).toContain("3 min");
    fireEvent.click(getByText("SSO is here!"));
    expect(onClick).toHaveBeenCalled();
  });
});
