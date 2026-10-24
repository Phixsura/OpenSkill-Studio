import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcCatalogBrowser } from "@/components/svc-catalog-browser";

describe("SvcCatalogBrowser", () => {
  it("renders", () => {
    const { container } = render(
      <SvcCatalogBrowser total={3}
        services={[
          { name: "auth-svc", owner: "team-a", tier: "critical", tags: ["auth"], dependencies: ["db"] },
          { name: "user-svc", owner: "team-b", tier: "standard", tags: ["users"], dependencies: [] },
        ]} />
    );
    expect(container.textContent).toContain("Service Catalog");
    expect(container.textContent).toContain("3 services");
    expect(container.textContent).toContain("auth-svc");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("team-a");
    expect(container.textContent).toContain("deps: db");
  });
});
