import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppInstallWizard } from "@/components/app-install-wizard";

const MOCK_APP = {
  id: "app-1",
  name: "LMS Connector",
  icon: "🔗",
  publisher: "EduTech Inc",
  version: "2.1.0",
  description: "Sync courses and grades with your LMS.",
  permissions: [
    { scope: "read:cohorts", description: "View cohorts", risk: "low" as const },
    { scope: "write:submissions", description: "Submit grades", risk: "medium" as const },
  ],
  config_fields: [
    {
      name: "lms_url",
      label: "LMS URL",
      type: "url" as const,
      required: true,
      default_value: "",
      description: "Your LMS base URL",
    },
    {
      name: "sync_mode",
      label: "Sync Mode",
      type: "enum" as const,
      required: true,
      default_value: "manual",
      description: "How to sync",
      enum_values: ["manual", "auto", "scheduled"],
    },
    {
      name: "notify",
      label: "Notifications",
      type: "boolean" as const,
      required: false,
      default_value: "true",
      description: "Send notifications",
    },
  ],
};

describe("AppInstallWizard", () => {
  it("renders app name and version", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    expect(container.textContent).toContain("Install LMS Connector");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("EduTech Inc");
  });

  it("renders step indicators", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    expect(container.textContent).toContain("Review");
    expect(container.textContent).toContain("Permissions");
    expect(container.textContent).toContain("Configure");
    expect(container.textContent).toContain("Install");
  });

  it("shows review step initially", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    expect(container.textContent).toContain("About this app");
    expect(container.textContent).toContain("Sync courses and grades");
  });

  it("navigates to permissions step on Next", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    const nextBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Next",
    );
    fireEvent.click(nextBtn!);
    expect(container.textContent).toContain("Requested Permissions");
    expect(container.textContent).toContain("read:cohorts");
    expect(container.textContent).toContain("write:submissions");
  });

  it("blocks Next until permissions accepted", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    // Go to permissions
    const nextBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Next",
    )!;
    fireEvent.click(nextBtn);
    // Next should be disabled
    const nextBtn2 = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Next",
    )!;
    expect(nextBtn2.disabled).toBe(true);
    // Accept permissions
    const checkbox = container.querySelector("input[type='checkbox']")!;
    fireEvent.click(checkbox);
    // Now Next should work
    const nextBtn3 = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Next",
    )!;
    expect(nextBtn3.disabled).toBe(false);
  });

  it("shows configure step with fields", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    // Navigate: Review → Permissions → accept → Configure
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(container.querySelector("input[type='checkbox']")!);
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    expect(container.textContent).toContain("Configuration");
    expect(container.textContent).toContain("LMS URL");
    expect(container.textContent).toContain("Sync Mode");
    expect(container.textContent).toContain("Notifications");
  });

  it("shows confirm step and Install button", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    // Navigate all the way through
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(container.querySelector("input[type='checkbox']")!);
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    expect(container.textContent).toContain("Ready to install");
    const installBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Install App",
    );
    expect(installBtn).toBeTruthy();
  });

  it("calls onInstall with config on Install", () => {
    const onInstall = vi.fn();
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={onInstall} onCancel={vi.fn()} />,
    );
    // Navigate to confirm
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(container.querySelector("input[type='checkbox']")!);
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find(
        (b) => b.textContent === "Install App",
      )!,
    );
    expect(onInstall).toHaveBeenCalledOnce();
    expect(onInstall).toHaveBeenCalledWith(expect.objectContaining({ sync_mode: "manual" }));
  });

  it("calls onCancel on first step Cancel", () => {
    const onCancel = vi.fn();
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={onCancel} />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Cancel")!,
    );
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("shows Back button on non-first steps", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    const backBtn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Back",
    );
    expect(backBtn).toBeTruthy();
  });

  it("goes back on Back click", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    expect(container.textContent).toContain("Requested Permissions");
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Back")!,
    );
    expect(container.textContent).toContain("About this app");
  });

  it("shows installing state", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} installing />,
    );
    // Navigate to confirm
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(container.querySelector("input[type='checkbox']")!);
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    expect(container.textContent).toContain("Installing…");
  });

  it("renders risk levels for permissions", () => {
    const { container } = render(
      <AppInstallWizard app={MOCK_APP} onInstall={vi.fn()} onCancel={vi.fn()} />,
    );
    fireEvent.click(
      Array.from(container.querySelectorAll("button")).find((b) => b.textContent === "Next")!,
    );
    expect(container.textContent).toContain("LOW");
    expect(container.textContent).toContain("MEDIUM");
  });
});
