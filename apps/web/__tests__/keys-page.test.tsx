import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KeysPage } from "@/components/keys-page";

describe("KeysPage", () => {
  const keys = [
    { prefix: "osk_abc", name: "Prod", scopes: ["read"], revoked: false, requests30d: 5000, lastUsed: "2026-01-01" },
  ];
  it("renders keys page", () => {
    const { container } = render(
      <KeysPage appName="SuperApp" keys={keys} active={1} totalRequests30d={5000}
        canCreate={true} onRevoke={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp — API Keys");
    expect(container.textContent).toContain("osk_abc");
    expect(container.textContent).toContain("Prod");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("+ New Key");
  });
});
