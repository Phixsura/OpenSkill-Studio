import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ThemeTokenPreview } from "@/components/theme-token-preview";

describe("ThemeTokenPreview", () => {
  const tokens = { "bg-primary": "#ffffff", "accent": "#3b82f6", "error": "#ef4444" };
  it("renders", () => {
    const { container } = render(<ThemeTokenPreview theme="light" tokens={tokens} />);
    expect(container.textContent).toContain("Theme Tokens — light");
    expect(container.textContent).toContain("bg-primary");
    expect(container.textContent).toContain("#ffffff");
    expect(container.textContent).toContain("accent");
    expect(container.textContent).toContain("#3b82f6");
  });
});
