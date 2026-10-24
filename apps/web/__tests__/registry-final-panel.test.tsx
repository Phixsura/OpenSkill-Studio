import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RegistryFinalPanel } from "@/components/registry-final-panel";
describe("RegistryFinalPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RegistryFinalPanel totalServices={50} modules={10} active={48} allActive={false}
        byModule={{ security: 5, core: 10, infra: 8, observability: 7 }} />
    );
    expect(container.textContent).toContain("Service Registry");
    expect(container.textContent).toContain("50 services");
    expect(container.textContent).toContain("10 modules");
    expect(container.textContent).toContain("48 active");
    expect(container.textContent).toContain("security: 5");
    expect(container.textContent).toContain("core: 10");
  });
});
