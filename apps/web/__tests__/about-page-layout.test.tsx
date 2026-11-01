import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AboutPageLayout } from "@/components/about-page-layout";

describe("AboutPageLayout", () => {
  it("renders", () => {
    const stats = [{ label: "Apps", value: 500, icon: "📦" }];
    const values = [{ title: "Developer First", description: "Dev experience matters", icon: "💻" }];
    const { container } = render(
      <AboutPageLayout title="About Us" subtitle="Building the future"
        mission="Democratize development" stats={stats} values={values} />
    );
    expect(container.textContent).toContain("About Us");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("Democratize development");
    expect(container.textContent).toContain("Developer First");
  });
});
