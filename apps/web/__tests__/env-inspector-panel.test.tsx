import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvInspectorPanel } from "@/components/env-inspector-panel";

const props = {
  summary: { runtime: "node 20.10", packages: 25, apis: 8, envVars: 5, issues: 1 },
  packages: [
    { name: "express", version: "4.18.0", sizeKb: 500 },
    { name: "lodash", version: "4.17.21", sizeKb: 1200 },
  ],
  availableApis: ["fetch", "crypto", "url", "path"],
  diagnostics: ["CPU at 85% capacity"],
};

describe("EnvInspectorPanel", () => {
  it("renders summary", () => {
    const { container } = render(<EnvInspectorPanel {...props} />);
    expect(container.textContent).toContain("node 20.10");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("8");
  });

  it("shows packages tab with search", () => {
    const { getByPlaceholderText, container } = render(<EnvInspectorPanel {...props} />);
    const tabs = container.querySelectorAll("button"); const pkgTab = Array.from(tabs).find(b => b.textContent === "Packages" && b.className.includes("rounded-lg")); if (pkgTab) fireEvent.click(pkgTab);
    expect(container.textContent).toContain("express");
    fireEvent.change(getByPlaceholderText("Search packages..."), { target: { value: "lodash" } });
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).not.toContain("express");
  });

  it("shows APIs as tags", () => {
    const { getByText, container } = render(<EnvInspectorPanel {...props} />);
    fireEvent.click(getByText("Apis"));
    expect(container.textContent).toContain("fetch");
    expect(container.textContent).toContain("crypto");
  });

  it("shows diagnostics", () => {
    const { getByText, container } = render(<EnvInspectorPanel {...props} />);
    fireEvent.click(getByText("Issues (1)"));
    expect(container.textContent).toContain("CPU at 85%");
  });
});
