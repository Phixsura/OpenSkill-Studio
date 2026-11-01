import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusPageCard } from "@/components/status-page-card";

const SERVICES = [{ name: "API", status: "operational", uptimePct: 99.99 }, { name: "Webhooks", status: "degraded", uptimePct: 98 }];

describe("StatusPageCard", () => {
  it("shows overall status", () => {
    const { container } = render(<StatusPageCard overall="operational" services={SERVICES} uptimePct={99} />);
    expect(container.textContent).toContain("operational");
    expect(container.textContent).toContain("🟢");
  });
  it("shows services", () => {
    const { container } = render(<StatusPageCard overall="degraded" services={SERVICES} uptimePct={98} />);
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("Webhooks");
  });
  it("shows uptime", () => {
    const { container } = render(<StatusPageCard overall="operational" services={[]} uptimePct={99.5} />);
    expect(container.textContent).toContain("99.5%");
  });
});
