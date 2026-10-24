import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatusPage } from "@/components/platform-status-page";

describe("PlatformStatusPage", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformStatusPage overall="partial_outage" operational={2} total={3}
        groups={{
          Core: [{ name: "API", status: "operational" }, { name: "DB", status: "outage" }],
          Web: [{ name: "Dashboard", status: "operational" }],
        }} />
    );
    expect(container.textContent).toContain("Partial Outage");
    expect(container.textContent).toContain("2/3 operational");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("DB");
    expect(container.textContent).toContain("Core");
  });
});
