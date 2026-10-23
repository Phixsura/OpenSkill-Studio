import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccessTokenList } from "@/components/access-token-list";

describe("AccessTokenList", () => {
  it("renders tokens", () => {
    const onRevoke = vi.fn();
    const { container, getByText } = render(
      <AccessTokenList onCreate={vi.fn()} onRevoke={onRevoke} tokens={[
        { name: "CI", prefix: "abc12345", scopes: ["read", "write"], revoked: false },
        { name: "Old", prefix: "xyz99999", scopes: ["read"], revoked: true },
      ]} />
    );
    expect(container.textContent).toContain("Access Tokens");
    expect(container.textContent).toContain("CI");
    expect(container.textContent).toContain("abc12345");
    expect(container.textContent).toContain("Revoked");
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("abc12345");
  });
});
