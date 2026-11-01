import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigEncryptionStatus } from "@/components/config-encryption-status";

describe("ConfigEncryptionStatus", () => {
  it("renders status", () => {
    const { container } = render(
      <ConfigEncryptionStatus totalFields={5} encryptedFields={3}
        unencryptedSensitive={["db_pass", "api_key"]} onEncrypt={vi.fn()} />
    );
    expect(container.textContent).toContain("Config Encryption");
    expect(container.textContent).toContain("3/5 encrypted");
    expect(container.textContent).toContain("db_pass");
    expect(container.textContent).toContain("api_key");
    expect(container.textContent).toContain("Unencrypted");
  });
});
