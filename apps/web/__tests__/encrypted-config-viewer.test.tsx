import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EncryptedConfigViewer } from "@/components/encrypted-config-viewer";

describe("EncryptedConfigViewer", () => {
  it("renders config", () => {
    const config = { app_name: "MyApp", db_password: "encrypted:abc", api_key: "encrypted:xyz" };
    const { container } = render(
      <EncryptedConfigViewer config={config} encryptedFields={["db_password", "api_key"]} onDecrypt={vi.fn()} />
    );
    expect(container.textContent).toContain("app_name");
    expect(container.textContent).toContain("MyApp");
    expect(container.textContent).toContain("encrypted");
    expect(container.textContent).toContain("Reveal");
  });
  it("decrypt button", () => {
    const fn = vi.fn();
    const { container } = render(
      <EncryptedConfigViewer config={{ secret: "enc" }} encryptedFields={["secret"]} onDecrypt={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Reveal")!);
    expect(fn).toHaveBeenCalledWith("secret");
  });
});
