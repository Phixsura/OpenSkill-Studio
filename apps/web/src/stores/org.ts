import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface OrgInfo {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  role: string | null;
  member_count: number;
  created_at: string;
}

interface OrgState {
  currentOrgId: string | null;
  currentOrg: OrgInfo | null;
  setCurrentOrg: (org: OrgInfo) => void;
  clearOrg: () => void;
}

export const useOrgStore = create<OrgState>()(
  persist(
    (set) => ({
      currentOrgId: null,
      currentOrg: null,
      setCurrentOrg: (org) => set({ currentOrgId: org.id, currentOrg: org }),
      clearOrg: () => set({ currentOrgId: null, currentOrg: null }),
    }),
    { name: "openskill-org" },
  ),
);
