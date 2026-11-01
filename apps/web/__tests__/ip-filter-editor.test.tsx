import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IpFilterEditor } from "@/components/ip-filter-editor";

describe("IpFilterEditor", () => {
  it("renders filter", () => {
    const onRemove = vi.fn();
    const { container, getAllByText } = render(
      <IpFilterEditor allowlist={["10.0.0.0/8"]} platformIps={["203.0.113.0/24"]}
        onAdd={vi.fn()} onRemove={onRemove} onAddPlatform={vi.fn()} />
    );
    expect(container.textContent).toContain("IP Filter");
    expect(container.textContent).toContain("10.0.0.0/8");
    expect(container.textContent).toContain("Add OpenSkill platform IPs");
    fireEvent.click(getAllByText("×")[0]);
    expect(onRemove).toHaveBeenCalledWith("10.0.0.0/8");
  });
});
