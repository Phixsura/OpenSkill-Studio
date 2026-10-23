import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LinkPreviewCard } from "@/components/link-preview-card";

describe("LinkPreviewCard", () => {
  it("renders", () => {
    const { container } = render(
      <LinkPreviewCard url="https://example.com" title="Auth SDK"
        description="Best auth solution" imageUrl="https://cdn.dev/img.png"
        domain="example.com" hasImage={true} onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("example.com");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Best auth solution");
  });
});
