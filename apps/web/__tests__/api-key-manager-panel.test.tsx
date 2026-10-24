import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyManagerPanel } from "@/components/api-key-manager-panel";

describe("ApiKeyManagerPanel", () => {
  it("renders keys", () => {
    const { container } = render(
      <ApiKeyManagerPanel onCreate={vi.fn()} onRevoke={vi.fn()} keys={[
        { name: "Production", prefix: "osk_abc1", scopes: ["read", "write"], revoked: false },
        { name: "Old Key", prefix: "osk_xyz9", scopes: ["read"], revoked: true },
      ]} />
    );
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("osk_abc1");
    expect(container.textContent).toContain("Revoked");
    expect(container.textContent).toContain("New Key");
  });
});
