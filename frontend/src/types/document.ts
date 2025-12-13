export interface RoutedDocument {
  predicted_label: string;
  probability: number | null;
  route_to: string;
  stored_at: string;
  note: string;
}
