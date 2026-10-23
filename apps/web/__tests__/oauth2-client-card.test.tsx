import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OAuth2ClientCard } from "@/components/oauth2-client-card";

describe("OAuth2ClientCard", () => {
  it("renders clients", () => {
    const onRevoke = vi.fn();
    const { container, getByText } = render(
      <OAuth2ClientCard onRevoke={onRevoke} clients={[
        { clientId: "osk_abc123", name: "MyApp", scopes: ["read", "write"], active: true },
        { clientId: "osk_xyz789", name: "OldApp", scopes: ["read"], active: false },
      ]} />
    );
    expect(container.textContent).toContain("OAuth2 Clients");
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("osk_abc123");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("Revoked");
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("osk_abc123");
  });
});
