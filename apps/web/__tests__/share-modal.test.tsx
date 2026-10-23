import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ShareModal } from "@/components/share-modal";

describe("ShareModal", () => {
  const platforms = [
    { id: "twitter", label: "Twitter", icon: "𝕏", url: "https://twitter.com/intent" },
    { id: "email", label: "Email", icon: "📧", url: "mailto:?subject=App" },
  ];
  it("renders", () => {
    const { container } = render(
      <ShareModal appName="Auth SDK" platforms={platforms} copyUrl="https://x.com/auth"
        embedCode='<a href="x">Auth</a>' onClose={vi.fn()} />
    );
    expect(container.textContent).toContain("Share Auth SDK");
    expect(container.textContent).toContain("𝕏");
    expect(container.textContent).toContain("Twitter");
    expect(container.textContent).toContain("📧");
    expect(container.textContent).toContain("Copy");
  });
});
