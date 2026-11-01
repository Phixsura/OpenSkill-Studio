import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CspConfigEditor } from "@/components/csp-config-editor";

describe("CspConfigEditor", () => {
  it("renders checkboxes", () => {
    const { container } = render(
      <CspConfigEditor allowEval={false} allowInline={true} origins={["https://api.com"]}
        onToggleEval={vi.fn()} onToggleInline={vi.fn()} />
    );
    expect(container.textContent).toContain("Content Security Policy");
    expect(container.textContent).toContain("https://api.com");
  });
  it("toggles eval", () => {
    const fn = vi.fn();
    const { container } = render(
      <CspConfigEditor allowEval={false} allowInline={false} origins={[]}
        onToggleEval={fn} onToggleInline={vi.fn()} />
    );
    const checkboxes = container.querySelectorAll("input[type='checkbox']");
    fireEvent.click(checkboxes[0]);
    expect(fn).toHaveBeenCalledWith(true);
  });
});
