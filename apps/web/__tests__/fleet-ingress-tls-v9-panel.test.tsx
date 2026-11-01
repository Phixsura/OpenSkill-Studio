import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIngressTlsV9Panel } from "@/components/fleet-ingress-tls-v9-panel";
describe("FleetIngressTlsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetIngressTlsV9Panel ingresses={30} tls={30} />);
    expect(container.textContent).toContain("Ingress TLS v9");
}); });
