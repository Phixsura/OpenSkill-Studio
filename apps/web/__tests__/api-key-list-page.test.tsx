import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyListPage } from "@/components/api-key-list-page";

describe("ApiKeyListPage", () => {
  const keys = [
    { prefix: "osk_abc", name: "Prod", scopes: ["read"], createdAt: "2026-01-01",
      lastUsed: "2026-01-03", revoked: false, requests30d: 5000 },
  ];
  it("renders keys", () => {
    const { container } = render(
      <ApiKeyListPage keys={keys} active={1} onRevoke={vi.fn()} onCreateNew={vi.fn()} />
    );
    expect(container.textContent).toContain("API Keys");
    expect(container.textContent).toContain("osk_abc");
    expect(container.textContent).toContain("Prod");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("+ New Key");
  });
});
