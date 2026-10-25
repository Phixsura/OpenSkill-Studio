import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionPermissionsDialog } from "@/components/extension-permissions-dialog";

const mockPermissions = [
  { key: "projects.read", label: "Read Projects", description: "View project data", level: "read" as const, required: true },
  { key: "users.read", label: "Read Users", description: "View user profiles", level: "read" as const, required: false },
  { key: "webhooks.manage", label: "Manage Webhooks", description: "Create and delete webhooks", level: "admin" as const, required: false },
];

describe("ExtensionPermissionsDialog", () => {
  it("renders extension name and permissions", () => {
    const { container } = render(
      <ExtensionPermissionsDialog extensionName="Slack Bot" permissions={mockPermissions} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Read Projects");
    expect(container.textContent).toContain("Manage Webhooks");
    expect(container.textContent).toContain("required");
  });

  it("required permissions are pre-checked and non-toggleable", () => {
    const { container } = render(
      <ExtensionPermissionsDialog extensionName="Test" permissions={mockPermissions} />
    );
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    expect((checkboxes[0] as HTMLInputElement).checked).toBe(true);
    expect((checkboxes[0] as HTMLInputElement).disabled).toBe(true);
  });

  it("calls onApprove with selected permissions", () => {
    const onApprove = vi.fn();
    const { getByText } = render(
      <ExtensionPermissionsDialog extensionName="Test" permissions={mockPermissions} onApprove={onApprove} />
    );
    fireEvent.click(getByText(/Approve/));
    expect(onApprove).toHaveBeenCalledWith(["projects.read"]);
  });

  it("shows level badges", () => {
    const { container } = render(
      <ExtensionPermissionsDialog extensionName="Test" permissions={mockPermissions} />
    );
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("admin");
  });
});
