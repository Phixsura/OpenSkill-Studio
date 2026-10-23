import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewCard } from "@/components/review-card";

describe("ReviewCard", () => {
  it("renders", () => {
    const { container } = render(
      <ReviewCard author="Alice" avatarInitials="AS" rating={5} stars="★★★★★"
        title="Amazing!" body="Best SDK ever." helpfulCount={12} dateDisplay="2026-10-23"
        hasResponse={false} developerResponse={null} onHelpful={vi.fn()} />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("AS");
    expect(container.textContent).toContain("★★★★★");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Best SDK ever.");
    expect(container.textContent).toContain("Helpful (12)");
  });
  it("renders with response", () => {
    const { container } = render(
      <ReviewCard author="Bob" avatarInitials="B" rating={3} stars="★★★"
        title="OK" body="Decent." helpfulCount={0} dateDisplay="2026-10-20"
        hasResponse={true} developerResponse="Thanks!" onHelpful={vi.fn()} />
    );
    expect(container.textContent).toContain("Developer Response");
    expect(container.textContent).toContain("Thanks!");
  });
  it("helpful click", () => {
    const fn = vi.fn();
    const { container } = render(
      <ReviewCard author="X" avatarInitials="X" rating={4} stars="★★★★"
        title="Good" body="Nice app." helpfulCount={5} dateDisplay="2026-10-23"
        hasResponse={false} developerResponse={null} onHelpful={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Helpful"))!);
    expect(fn).toHaveBeenCalled();
  });
});
