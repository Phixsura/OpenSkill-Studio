import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyIllustration } from "@/components/empty-illustration";

describe("EmptyIllustration", () => {
  it("shows icon and title", () => {
    const { container } = render(<EmptyIllustration icon="📦" title="No apps yet" />);
    expect(container.textContent).toContain("📦");
    expect(container.textContent).toContain("No apps yet");
  });
  it("shows subtitle", () => {
    const { container } = render(<EmptyIllustration icon="🔍" title="No results" subtitle="Try a different search" />);
    expect(container.textContent).toContain("Try a different");
  });
});
