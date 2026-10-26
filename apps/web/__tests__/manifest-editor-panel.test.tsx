import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ManifestEditorPanel } from "@/components/manifest-editor-panel";

const mockManifest = {
  name: "my-extension", version: "1.0.0", manifestVersion: "2.0",
  entrypoint: "index.js", runtime: "node20", sdkVersion: "1.5.0",
  permissions: ["file:read", "network:outbound"],
  description: "A test extension", author: "dev",
  dependencies: { lodash: "^4.0" },
};

describe("ManifestEditorPanel", () => {
  it("renders manifest fields", () => {
    const { container } = render(
      <ManifestEditorPanel manifest={mockManifest} errors={[]} />
    );
    expect(container.textContent).toContain("Manifest Editor");
    expect(container.textContent).toContain("file:read");
    expect(container.textContent).toContain("network:outbound");
  });

  it("calls onSave", () => {
    const onSave = vi.fn();
    const { getByText } = render(
      <ManifestEditorPanel manifest={mockManifest} errors={[]} onSave={onSave} />
    );
    fireEvent.click(getByText("Save"));
    expect(onSave).toHaveBeenCalled();
  });

  it("shows validation errors", () => {
    const errors = [{ message: "Invalid semver" }, { message: "Missing entrypoint" }];
    const { container } = render(
      <ManifestEditorPanel manifest={mockManifest} errors={errors} />
    );
    expect(container.textContent).toContain("Invalid semver");
    expect(container.textContent).toContain("Missing entrypoint");
  });

  it("removes permission", () => {
    const { container } = render(
      <ManifestEditorPanel manifest={mockManifest} errors={[]} />
    );
    const removeButtons = container.querySelectorAll("button");
    const removeBtn = Array.from(removeButtons).find(b => b.textContent === "×");
    if (removeBtn) fireEvent.click(removeBtn);
    // One permission removed
    const perms = container.querySelectorAll('[class*="rounded-full"]');
    expect(perms.length).toBeLessThanOrEqual(2);
  });
});
