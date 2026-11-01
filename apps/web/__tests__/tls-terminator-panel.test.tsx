import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TlsTerminatorPanel } from "@/components/tls-terminator-panel";
describe("TlsTerminatorPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TlsTerminatorPanel totalConnections={50000} expiringSoon={1}
        certs={[
          { domain: "api.example.com", expiresDays: 90, active: true },
          { domain: "web.example.com", expiresDays: 15, active: true },
        ]} />
    );
    expect(container.textContent).toContain("TLS Termination");
    expect(container.textContent).toContain("2 certs");
    expect(container.textContent).toContain("50,000 conn");
    expect(container.textContent).toContain("1 expiring");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("90d left");
    expect(container.textContent).toContain("15d left");
  });
});
