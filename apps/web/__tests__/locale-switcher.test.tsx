import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LocaleSwitcher } from "@/components/locale-switcher";

const locales = [
  { locale: "en", label: "English", completeness: 100 },
  { locale: "zh", label: "中文", completeness: 33 },
  { locale: "ja", label: "日本語", completeness: 0 },
];

describe("LocaleSwitcher", () => {
  it("renders locales with flags", () => {
    const { container } = render(<LocaleSwitcher locales={locales} selected="en" />);
    expect(container.textContent).toContain("English");
    expect(container.textContent).toContain("中文");
    expect(container.textContent).toContain("33%");
  });
  it("selects locale", () => {
    const fn = vi.fn();
    const { container } = render(<LocaleSwitcher locales={locales} selected="en" onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]);
    expect(fn).toHaveBeenCalledWith("zh");
  });
});
