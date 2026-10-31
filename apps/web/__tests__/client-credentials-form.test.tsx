import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClientCredentialsForm } from "@/components/client-credentials-form";

describe("ClientCredentialsForm", () => {
  it("shows client id", () => {
    const { container } = render(<ClientCredentialsForm clientId="osk_abc123" onRegenerate={vi.fn()} />);
    expect(container.textContent).toContain("osk_abc123");
  });

  it("masks secret by default", () => {
    const { container } = render(<ClientCredentialsForm clientId="x" clientSecret="supersecret" onRegenerate={vi.fn()} />);
    expect(container.textContent).toContain("••••");
    expect(container.textContent).not.toContain("supersecret");
  });

  it("shows warning for secret", () => {
    const { container } = render(<ClientCredentialsForm clientId="x" clientSecret="s" onRegenerate={vi.fn()} />);
    expect(container.textContent).toContain("shown once");
  });

  it("has regenerate button", () => {
    const { container } = render(<ClientCredentialsForm clientId="x" onRegenerate={vi.fn()} />);
    expect(container.textContent).toContain("Regenerate");
  });
});
