import type { RoutedDocument } from "../types/document";
import DocumentCard from "./DocumentCard";
import { useState } from "react";

interface Props {
  documents: RoutedDocument[];
}

const DEPARTMENTS = ["finance", "admin", "manual_review"];

export default function DepartmentTabs({ documents }: Props) {
  const [active, setActive] = useState("finance");

  return (
    <>
      <div className="tabs">
        {DEPARTMENTS.map(dep => (
          <button
            key={dep}
            className={active === dep ? "active" : ""}
            onClick={() => setActive(dep)}
          >
            {dep.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {documents
          .filter(d => d.route_to === active)
          .map((doc, idx) => (
            <DocumentCard key={idx} doc={doc} />
          ))}
      </div>
    </>
  );
}
