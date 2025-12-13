import axios from "axios";
import { useState } from "react";
import type { RoutedDocument } from "../types/document";

interface UploadPanelProps {
  onUploaded: (doc: RoutedDocument) => void;
}

export default function UploadPanel({ onUploaded }: UploadPanelProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/ingest", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onUploaded(res.data);
      setFile(null);
    } catch (err) {
      setError("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-panel">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload Document"}
      </button>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
