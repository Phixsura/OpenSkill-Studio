import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CorsConfigEditor } from "@/components/cors-config-editor";

describe("CorsConfigEditor", () => {
  it("renders", () => {
    const { container } = render(
      <CorsConfigEditor origins={["https://example.com"]} methods={["GET", "POST"]}
        maxAgeSec={3600} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("CORS Configuration");
    expect(container.textContent).toContain("https://example.com");
    expect(container.textContent).toContain("Allowed Methods");
    expect(container.textContent).toContain("Save CORS Config");
  });
  it("save", () => {
    const fn = vi.fn();
    const { container } = render(
      <CorsConfigEditor origins={["*"]} methods={["GET"]} maxAgeSec={3600} onSave={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Save CORS Config")!);
    expect(fn).toHaveBeenCalled();
  });
});
