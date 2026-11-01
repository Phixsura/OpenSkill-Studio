import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionSharePanel } from "@/components/extension-share-panel";

const props = {
  shareUrl: "https://marketplace.openskill.dev/ext/ext-1?ref=abc",
  embedCode: '<iframe src="..." width="300" height="200"></iframe>',
  stats: { views: 500, installs: 50, conversionRate: 10 },
  social: { twitter: "https://twitter.com/intent/tweet?text=...", linkedin: "https://linkedin.com/...", copyLink: "https://..." },
};

describe("ExtensionSharePanel", () => {
  it("renders share stats", () => {
    const { container } = render(<ExtensionSharePanel {...props} />);
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("10%");
  });
  it("shows embed code", () => {
    const { getByText, container } = render(<ExtensionSharePanel {...props} />);
    fireEvent.click(getByText("📋 Embed"));
    expect(container.textContent).toContain("iframe");
  });
  it("calls onCopyLink", () => {
    const fn = vi.fn();
    const { getByText } = render(<ExtensionSharePanel {...props} onCopyLink={fn} />);
    fireEvent.click(getByText("Copy"));
    expect(fn).toHaveBeenCalled();
  });
});
