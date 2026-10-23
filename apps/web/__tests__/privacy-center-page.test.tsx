import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PrivacyCenterPage } from "@/components/privacy-center-page";

describe("PrivacyCenterPage", () => {
  const sections = [
    { key: "rights", title: "Your Rights", icon: "⚖️", rights: ["Access data", "Delete data"] },
    { key: "data", title: "Your Data", icon: "📋" },
    { key: "delete", title: "Delete Account", icon: "🗑️", warning: "Permanent action" },
  ];
  it("renders", () => {
    const { container } = render(
      <PrivacyCenterPage userName="Alice" sections={sections} onExportData={vi.fn()} onDeleteAccount={vi.fn()} />
    );
    expect(container.textContent).toContain("Privacy Center");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Access data");
    expect(container.textContent).toContain("Export My Data");
    expect(container.textContent).toContain("Permanent action");
  });
  it("export data", () => {
    const fn = vi.fn();
    const { container } = render(
      <PrivacyCenterPage userName="X" sections={sections} onExportData={fn} onDeleteAccount={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Export"))!);
    expect(fn).toHaveBeenCalled();
  });
});
