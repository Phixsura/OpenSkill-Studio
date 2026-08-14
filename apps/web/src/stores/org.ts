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
