import { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import DepartmentTabs from "./components/DepartmentTabs";
import type { RoutedDocument } from "./types/document";

import "./App.css";

export default function App() {
  const [documents, setDocuments] = useState<RoutedDocument[]>([]);

  return (
    <div className="app">
      <h1 className="app-title">IDMS – Intelligent Document Router</h1>

      <UploadPanel
        onUploaded={(doc) =>
          setDocuments((prev) => [...prev, doc])
        }
      />

      <DepartmentTabs documents={documents} />
    </div>
  );
}
