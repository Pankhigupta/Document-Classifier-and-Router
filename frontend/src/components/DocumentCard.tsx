import type { RoutedDocument } from "../types/document";

interface Props {
  doc: RoutedDocument;
}

export default function DocumentCard({ doc }: Props) {
  const fileUrl = `http://localhost:8000/files/${doc.route_to}/${doc.stored_at.split("/").pop()}`;

  return (
    <div className="doc-card">
      <p><strong>Type:</strong> {doc.predicted_label}</p>
      <p><strong>Confidence:</strong> {doc.probability?.toFixed(2)}</p>
      <a href={fileUrl} target="_blank">Open Document</a>
    </div>
  );
}
