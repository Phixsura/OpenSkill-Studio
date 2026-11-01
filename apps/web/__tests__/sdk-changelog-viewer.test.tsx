import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SdkChangelogViewer } from "@/components/sdk-changelog-viewer";

describe("SdkChangelogViewer", () => {
  it("renders changelog", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <SdkChangelogViewer selectedLang="typescript" onSelectLang={onSelect}
        languages={["typescript", "python"]}
        releases={{
          typescript: [{ version: "3.5.0", date: "2026-10-24", changes: ["Added SSO"], breaking: false }],
          python: [{ version: "3.5.0", date: "2026-10-24", changes: ["Async"], breaking: true }],
        }} />
    );
    expect(container.textContent).toContain("SDK Changelog");
    expect(container.textContent).toContain("v3.5.0");
    expect(container.textContent).toContain("Added SSO");
    fireEvent.click(getByText(/python/));
    expect(onSelect).toHaveBeenCalledWith("python");
  });
});
