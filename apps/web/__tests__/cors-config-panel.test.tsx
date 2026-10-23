import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CorsConfigPanel } from "@/components/cors-config-panel";

describe("CorsConfigPanel", () => {
  it("renders config", () => {
    const { container } = render(
      <CorsConfigPanel origins={["https://example.com"]} methods={["GET", "POST"]}
        headers={["Content-Type"]} maxAgeS={86400} credentials={false} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("CORS Configuration");
    expect(container.textContent).toContain("https://example.com");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("86400s");
    expect(container.textContent).toContain("Save CORS Config");
  });
});
