import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IngressCtrlPanel } from "@/components/ingress-ctrl-panel";

describe("IngressCtrlPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IngressCtrlPanel tlsEnabled={2}
        rules={[
          { host: "api.example.com", path: "/v1", backend: "api-svc", tls: true },
          { host: "app.example.com", path: "/", backend: "web-svc", tls: true },
        ]}
        certs={[
          { domain: "api.example.com", expiresDays: 10, issuer: "letsencrypt" },
        ]} />
    );
    expect(container.textContent).toContain("Ingress Controller");
    expect(container.textContent).toContain("2 rules");
    expect(container.textContent).toContain("2 TLS");
    expect(container.textContent).toContain("api.example.com/v1");
    expect(container.textContent).toContain("api-svc");
    expect(container.textContent).toContain("expiring soon");
  });
});
