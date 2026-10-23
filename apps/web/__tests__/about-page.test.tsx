import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AboutPage } from "@/components/about-page";

describe("AboutPage", () => {
  const components = [
    { name: "API Server", version: "2.0.0", status: "operational" },
    { name: "Database", version: "PostgreSQL 16", status: "operational" },
  ];
  it("renders about page", () => {
    const { container } = render(
      <AboutPage appName="OpenSkill" version="2.0.0" runtime="Python 3.12"
        components={components} links={{ docs: "/docs", changelog: "/changelog" }} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("API Server");
    expect(container.textContent).toContain("docs");
  });
});
