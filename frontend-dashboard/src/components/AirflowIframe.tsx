// src/components/AirflowIframe.tsx

import React from "react";

type AirflowIframeProps = {
  /** Full Airflow URL to embed, e.g. https://airflow.yourdomain.com */
  url?: string;
};

const AirflowIframe: React.FC<AirflowIframeProps> = ({ url }) => {
  // Fallback to env or localhost if no prop passed
  const iframeUrl =
    url || import.meta.env.VITE_AIRFLOW_URL || "http://localhost:8080";

  return (
    <div className="airflow-iframe-container" style={{ height: "100%", width: "100%" }}>
      <iframe
        src={iframeUrl}
        title="Airflow UI"
        style={{
          border: "none",
          width: "100%",
          height: "100%",
        }}
      />
    </div>
  );
};

export default AirflowIframe;
