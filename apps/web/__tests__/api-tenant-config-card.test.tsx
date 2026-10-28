import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APITenantConfigCard from "../src/components/api-tenant-config-card";

const config = [
  { key: "theme", value: "dark", overridden: true },
  { key: "lang", value: "en", overridden: false },
];

describe("APITenantConfigCard", () => {
  it("renders header with tenant", () => {
    const { container } = render(<APITenantConfigCard config={config} tenantId="acme" overrideCount={1} appName="App" />);
    expect(container.textContent).toContain("Tenant Config");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("1 overrides");
  });

  it("shows keys with override badge", () => {
    const { container } = render(<APITenantConfigCard config={config} tenantId="acme" overrideCount={1} appName="App" />);
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("override");
    expect(container.textContent).toContain("dark");
  });

  it("shows empty state", () => {
    const { container } = render(<APITenantConfigCard config={[]} tenantId="x" overrideCount={0} appName="App" />);
    expect(container.textContent).toContain("No configuration");
  });
});
