/**
 * トーナメント関連の型定義
 */

export type TournamentStatus = 'draft' | 'entry_open' | 'entry_closed' | 'in_progress' | 'completed' | 'cancelled';

export const statusLabels: Record<TournamentStatus, string> = {
  draft: '下書き',
  entry_open: 'エントリー受付中',
  entry_closed: 'エントリー締切',
  in_progress: '開催中',
  completed: '終了',
  cancelled: 'キャンセル',
};

export const statusColors: Record<TournamentStatus, 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'> = {
  draft: 'default',
  entry_open: 'success',
  entry_closed: 'warning',
  in_progress: 'primary',
  completed: 'secondary',
  cancelled: 'error',
};

export interface EntryRestriction {
  min_players: number;
  max_players: number;
  min_class?: string;
  max_class?: string;
}

export interface Entry {
  player_id: string;
  team_id: string;
  entry_date: string;
  status: string;
  player_name?: string;
  team_name?: string;
}

export interface Tournament {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  entry_start_date: string;
  entry_end_date: string;
  venue: string;
  entry_fee: number;
  status: TournamentStatus;
  entry_restriction: EntryRestriction;
  entries: Entry[];
  current_entries: number;
  created_at: string;
  updated_at: string;
}

export interface TournamentListResponse {
  items: Tournament[];
  total: number;
} 