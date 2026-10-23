import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { A11yScoreBadge } from "@/components/a11y-score-badge";

describe("A11yScoreBadge", () => {
  const checks = [
    { id: "alt_text", label: "Alt text", category: "perceivable", passed: true },
    { id: "keyboard", label: "Keyboard nav", category: "operable", passed: false },
  ];
  it("renders", () => {
    const { container } = render(
      <A11yScoreBadge score={75} grade="B" checks={checks} passed={1} total={2} />
    );
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("1/2 checks");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
    expect(container.textContent).toContain("Alt text");
  });
});
