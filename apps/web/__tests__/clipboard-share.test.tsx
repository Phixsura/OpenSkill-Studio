import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClipboardShare } from "@/components/clipboard-share";

describe("ClipboardShare", () => {
  const options = [
    { label: "Direct Link", value: "https://example.com/app", icon: "🔗" },
    { label: "Markdown", value: "[MyApp](https://example.com)", icon: "📝" },
  ];
  it("renders share options", () => {
    const { container } = render(<ClipboardShare options={options} />);
    expect(container.textContent).toContain("Direct Link");
    expect(container.textContent).toContain("Markdown");
    expect(container.textContent).toContain("🔗");
    expect(container.querySelectorAll("button").length).toBe(2);
  });
});
