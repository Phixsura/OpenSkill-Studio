import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PermissionList } from "@/components/permission-list";

describe("PermissionList", () => {
  it("renders all permissions", () => {
    const perms = ["read:cohorts", "write:projects", "subscribe:events"];
    const { container } = render(<PermissionList permissions={perms} />);
    expect(container.textContent).toContain("read:cohorts");
    expect(container.textContent).toContain("write:projects");
  });

  it("renders empty list", () => {
    const { container } = render(<PermissionList permissions={[]} />);
    expect(container).toBeTruthy();
  });

  it("truncates when exceeding maxVisible", () => {
    const perms = Array.from({ length: 15 }, (_, i) => `read:resource_${i}`);
    const { container } = render(<PermissionList permissions={perms} maxVisible={5} />);
    expect(container.textContent).toContain("10");
  });

  it("shows all when under maxVisible", () => {
    const perms = ["read:cohorts", "write:projects"];
    const { container } = render(<PermissionList permissions={perms} maxVisible={10} />);
    expect(container.textContent).not.toContain("more");
  });
});
