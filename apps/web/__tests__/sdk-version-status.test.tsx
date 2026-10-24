import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SdkVersionStatus } from "@/components/sdk-version-status";

describe("SdkVersionStatus", () => {
  it("renders SDKs", () => {
    const onInstall = vi.fn();
    const { container, getAllByText } = render(
      <SdkVersionStatus onInstall={onInstall} sdks={[
        { language: "typescript", pkg: "@openskill/sdk", latest: "3.5.0" },
        { language: "python", pkg: "openskill-sdk", latest: "3.5.0" },
      ]} />
    );
    expect(container.textContent).toContain("SDKs");
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("@openskill/sdk");
    expect(container.textContent).toContain("v3.5.0");
    fireEvent.click(getAllByText("Install")[0]);
    expect(onInstall).toHaveBeenCalledWith("typescript");
  });
});
