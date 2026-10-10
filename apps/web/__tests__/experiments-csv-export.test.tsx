import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { CsvExportButton } from "@/app/(dashboard)/dashboard/experiments/components";

const apiText = vi.hoisted(() => vi.fn());
vi.mock("@/lib/api", () => ({ apiTextWithAuth: apiText }));

beforeEach(() => vi.clearAllMocks());

describe("CsvExportButton (round 134)", () => {
  it("fetches the export path with auth and triggers a blob download", async () => {
    apiText.mockResolvedValue("unit_type,unit_id\nuser,abc\n");
    const createObjectURL = vi.fn(() => "blob:fake");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", {
      ...URL,
      createObjectURL,
      revokeObjectURL,
    });
    const click = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);

    render(<CsvExportButton path="/experiments/E1/assignments/export" filename="a.csv" />);
    fireEvent.click(screen.getByText("Export CSV"));
    await waitFor(() => {
      expect(apiText).toHaveBeenCalledWith("/experiments/E1/assignments/export");
      expect(createObjectURL).toHaveBeenCalled();
      expect(click).toHaveBeenCalled();
      expect(revokeObjectURL).toHaveBeenCalledWith("blob:fake");
    });
    vi.unstubAllGlobals();
    click.mockRestore();
  });

  it("re-enables after a failed export (no stuck busy state)", async () => {
    apiText.mockRejectedValue(new Error("boom"));
    render(<CsvExportButton path="/x" filename="x.csv" />);
    fireEvent.click(screen.getByText("Export CSV"));
    const btn = await screen.findByText("Export failed — retry");
    expect((btn as HTMLButtonElement).disabled).toBe(false);
  });
});
