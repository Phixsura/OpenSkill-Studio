import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataEncryptPanel } from "@/components/data-encrypt-panel";

describe("DataEncryptPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DataEncryptPanel activeKey="primary" totalKeys={2}
        keys={[
          { name: "primary", version: 3, fingerprint: "abc123def456ab" },
          { name: "backup", version: 1, fingerprint: "xyz789abc012cd" },
        ]} />
    );
    expect(container.textContent).toContain("Encryption Keys");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("active: primary");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("abc123def456ab");
  });
});
