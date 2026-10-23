import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TermsAcceptanceBanner } from "@/components/terms-acceptance-banner";

describe("TermsAcceptanceBanner", () => {
  const pending = [{ document_type: "tos", version: "2.1", title: "Terms of Service", url: "https://x.com/tos" }];
  it("renders", () => {
    const { container } = render(<TermsAcceptanceBanner pending={pending} onAccept={vi.fn()} />);
    expect(container.textContent).toContain("Terms Update Required");
    expect(container.textContent).toContain("Terms of Service v2.1");
    expect(container.textContent).toContain("Read full document");
  });
  it("accept", () => {
    const fn = vi.fn();
    const { container } = render(<TermsAcceptanceBanner pending={pending} onAccept={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Accept")!);
    expect(fn).toHaveBeenCalledWith("tos", "2.1");
  });
  it("hidden when empty", () => {
    const { container } = render(<TermsAcceptanceBanner pending={[]} onAccept={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
