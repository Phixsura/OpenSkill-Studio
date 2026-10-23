import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OpenApiSpecViewer } from "@/components/openapi-spec-viewer";

describe("OpenApiSpecViewer", () => {
  const endpoints = [
    { path: "/apps", method: "GET", description: "List apps" },
    { path: "/apps", method: "POST", description: "Create app" },
  ];
  it("renders", () => {
    const { container } = render(
      <OpenApiSpecViewer appName="MyApp" version="1.0.0" endpoints={endpoints}
        pathCount={1} onDownload={vi.fn()} />
    );
    expect(container.textContent).toContain("MyApp API");
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/apps");
  });
  it("download", () => {
    const fn = vi.fn();
    const { container } = render(
      <OpenApiSpecViewer appName="X" version="1.0" endpoints={endpoints} pathCount={1} onDownload={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Download Spec")!);
    expect(fn).toHaveBeenCalled();
  });
});
