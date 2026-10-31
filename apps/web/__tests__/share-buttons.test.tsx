import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ShareButtons } from "@/components/share-buttons";

describe("ShareButtons", () => {
  it("renders buttons", () => {
    const { container } = render(
      <ShareButtons title="My App" twitter="https://twitter.com/intent/tweet?text=test"
        linkedin="https://linkedin.com/share" copyUrl="https://openskill.io/apps/test" />
    );
    expect(container.textContent).toContain("Share:");
    expect(container.textContent).toContain("Twitter");
    expect(container.textContent).toContain("LinkedIn");
    expect(container.textContent).toContain("Copy");
  });
});
