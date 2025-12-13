import axios from "axios";
import type { RoutedDocument } from "../types/document";

const API_BASE = "http://localhost:8000";

export async function uploadDocument(file: File): Promise<RoutedDocument> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post<RoutedDocument>(
    `${API_BASE}/ingest`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );

  return response.data;
}
