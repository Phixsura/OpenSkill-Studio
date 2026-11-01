import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusPageComponent } from "@/components/status-page-component";

const page = {
  title: "Auth Service Status", overall: "degraded", updatedAt: Date.now(),
  services: [
    { name: "API", status: "operational", uptimePct: 99.9 },
    { name: "Database", status: "degraded", uptimePct: 98.5 },
    { name: "Cache", status: "operational", uptimePct: 100 },
  ],
};

describe("StatusPageComponent", () => {
  it("renders status page", () => {
    const { container } = render(<StatusPageComponent page={page} />);
    expect(container.textContent).toContain("Auth Service Status");
    expect(container.textContent).toContain("Degraded");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("98.5%");
  });
});
