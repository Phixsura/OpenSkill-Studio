import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TlsConfigPanel } from "@/components/tls-config-panel";

describe("TlsConfigPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TlsConfigPanel minVersion="1.3" grade="A" secure={true}
        cipherCount={3} weakCiphers={[]} securePct={100} />
    );
    expect(container.textContent).toContain("TLS Configuration");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("TLS 1.3");
    expect(container.textContent).toContain("3 ciphers");
    expect(container.textContent).toContain("100%");
  });
});
