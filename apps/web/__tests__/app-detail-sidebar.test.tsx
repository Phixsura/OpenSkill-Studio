import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailSidebar } from "@/components/app-detail-sidebar";

describe("AppDetailSidebar", () => {
  const infoItems = [{ label: "Version", value: "2.1.0", icon: "📦" }];
  const links = [{ label: "Docs", url: "https://docs.example.com", icon: "📚" }];
  it("renders", () => {
    const { container } = render(
      <AppDetailSidebar infoItems={infoItems} links={links}
        permissions={["read:profile"]} tags={["auth", "oauth"]} />
    );
    expect(container.textContent).toContain("Information");
    expect(container.textContent).toContain("2.1.0");
    expect(container.textContent).toContain("Docs");
    expect(container.textContent).toContain("Permissions (1)");
    expect(container.textContent).toContain("read:profile");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("oauth");
  });
});
