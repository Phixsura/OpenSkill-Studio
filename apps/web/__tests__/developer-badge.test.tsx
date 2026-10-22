import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperBadge } from "@/components/developer-badge";

describe("DeveloperBadge", () => {
  it("renders name", () => {
    const { container } = render(<DeveloperBadge displayName="Studio Dev" />);
    expect(container.textContent).toContain("Studio Dev");
  });

  it("shows verified mark", () => {
    const { container } = render(<DeveloperBadge displayName="Dev" verified />);
    expect(container.textContent).toContain("✓");
  });

  it("hides verified when false", () => {
    const { container } = render(<DeveloperBadge displayName="Dev" />);
    expect(container.textContent).not.toContain("✓");
  });

  it("shows slug", () => {
    const { container } = render(<DeveloperBadge displayName="Dev" slug="dev-studio" />);
    expect(container.textContent).toContain("@dev-studio");
  });
});
