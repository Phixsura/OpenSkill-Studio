import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IsolationBoundaryPanel } from "@/components/isolation-boundary-panel";

const mockBoundaries = [
  { sandboxId: "sb-1", tenantId: "t1", isolationLevel: "full" as const,
    namespace: "ns_t1_abc", commPolicy: "allow_explicit" as const,
    allowedPeers: ["sb-2"], sharedVolumes: [] },
  { sandboxId: "sb-2", tenantId: "t1", isolationLevel: "namespace" as const,
    namespace: "ns_t1_def", commPolicy: "allow_same_tenant" as const,
    allowedPeers: [], sharedVolumes: ["/shared"] },
  { sandboxId: "sb-3", tenantId: "t2", isolationLevel: "shared" as const,
    namespace: "ns_t2_ghi", commPolicy: "deny_all" as const,
    allowedPeers: [], sharedVolumes: [] },
];

describe("IsolationBoundaryPanel", () => {
  it("renders current sandbox details", () => {
    const { container } = render(
      <IsolationBoundaryPanel boundaries={mockBoundaries} currentSandbox="sb-1" />
    );
    expect(container.textContent).toContain("Current: sb-1");
    expect(container.textContent).toContain("Full");
    expect(container.textContent).toContain("Explicit");
    expect(container.textContent).toContain("sb-2");
  });

  it("renders other sandboxes", () => {
    const { container } = render(
      <IsolationBoundaryPanel boundaries={mockBoundaries} currentSandbox="sb-1" />
    );
    expect(container.textContent).toContain("sb-3");
    expect(container.textContent).toContain("Shared");
  });

  it("calls onAllowPeer", () => {
    const onAllow = vi.fn();
    const { getAllByText } = render(
      <IsolationBoundaryPanel boundaries={mockBoundaries} currentSandbox="sb-1" onAllowPeer={onAllow} />
    );
    fireEvent.click(getAllByText("Allow")[0]);
    expect(onAllow).toHaveBeenCalled();
  });

  it("calls onCheckComm", () => {
    const onCheck = vi.fn();
    const { getAllByText } = render(
      <IsolationBoundaryPanel boundaries={mockBoundaries} currentSandbox="sb-1" onCheckComm={onCheck} />
    );
    fireEvent.click(getAllByText("Check")[0]);
    expect(onCheck).toHaveBeenCalled();
  });
});
