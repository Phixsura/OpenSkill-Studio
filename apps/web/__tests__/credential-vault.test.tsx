import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CredentialVault } from "@/components/credential-vault";

describe("CredentialVault", () => {
  const creds = [
    { id: "c1", name: "DB_PASSWORD", preview: "sup•••", status: "active", expiresAt: "2099-01-01" },
    { id: "c2", name: "API_KEY", preview: "sk-•••", status: "active", expiresAt: "2020-01-01" },
  ];
  it("renders credentials", () => {
    const { container } = render(
      <CredentialVault credentials={creds} expired={["API_KEY"]} expiringSoon={[]} onRotate={vi.fn()} />
    );
    expect(container.textContent).toContain("DB_PASSWORD");
    expect(container.textContent).toContain("API_KEY");
    expect(container.textContent).toContain("Expired");
    expect(container.textContent).toContain("1 need attention");
  });
  it("rotate click", () => {
    const fn = vi.fn();
    const { container } = render(
      <CredentialVault credentials={creds} expired={[]} expiringSoon={[]} onRotate={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("c1");
  });
});
