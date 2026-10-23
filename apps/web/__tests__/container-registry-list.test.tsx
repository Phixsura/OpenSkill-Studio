import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContainerRegistryList } from "@/components/container-registry-list";

describe("ContainerRegistryList", () => {
  const images = [
    { tag: "latest", digest: "sha256:abc123456789012", size_mb: 145, pushed_at: "2026-10-23" },
    { tag: "v2.0.0", digest: "sha256:def123456789012", size_mb: 142, pushed_at: "2026-10-22" },
  ];
  it("renders", () => {
    const { container } = render(
      <ContainerRegistryList repository="myapp/api" images={images} totalSizeMb={287}
        onDelete={vi.fn()} onPull={vi.fn()} />
    );
    expect(container.textContent).toContain("Container Registry");
    expect(container.textContent).toContain("myapp/api");
    expect(container.textContent).toContain("latest");
    expect(container.textContent).toContain("v2.0.0");
  });
  it("pull", () => {
    const fn = vi.fn();
    const { container } = render(
      <ContainerRegistryList repository="x" images={images} totalSizeMb={287}
        onDelete={vi.fn()} onPull={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Pull")!);
    expect(fn).toHaveBeenCalledWith("latest");
  });
});
