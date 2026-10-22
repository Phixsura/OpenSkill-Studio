import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiKeyDisplay } from "@/components/api-key-display";

const BASE = { keyPrefix: "osk_app_", name: "Production", scopes: ["read:cohorts"], createdAt: "2026-01-01" };

describe("ApiKeyDisplay", () => {
  it("renders name", () => {
    const { container } = render(<ApiKeyDisplay {...BASE} />);
    expect(container.textContent).toContain("Production");
  });

  it("shows masked key", () => {
    const { container } = render(<ApiKeyDisplay {...BASE} />);
    expect(container.textContent).toContain("osk_app_");
    expect(container.textContent).toContain("•");
  });

  it("shows raw key when provided", () => {
    const { container } = render(<ApiKeyDisplay {...BASE} rawKey="osk_app_abc123xyz" />);
    expect(container.textContent).toContain("osk_app_abc123xyz");
    expect(container.textContent).toContain("won't be shown");
  });

  it("shows scopes", () => {
    const { container } = render(<ApiKeyDisplay {...BASE} />);
    expect(container.textContent).toContain("read:cohorts");
  });

  it("shows revoke button", () => {
    const { container } = render(<ApiKeyDisplay {...BASE} onRevoke={vi.fn()} />);
    expect(container.textContent).toContain("Revoke");
  });

  it("shows created date", () => {
    const { container } = render(<ApiKeyDisplay {...BASE} />);
    expect(container.textContent).toContain("2026-01-01");
  });
});
