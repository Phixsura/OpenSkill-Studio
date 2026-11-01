import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiStatusWidget } from "@/components/api-status-widget";

describe("ApiStatusWidget", () => {
  it("renders widget", () => {
    const { container } = render(
      <ApiStatusWidget status="operational" icon="🟢" healthDisplay="5/5" latencyDisplay="65ms" />
    );
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("5/5");
    expect(container.textContent).toContain("65ms");
  });
});
