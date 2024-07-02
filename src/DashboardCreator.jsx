import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./DashboardCreator.css"; 

const DashboardCreator = () => {
  const [dashboardTitle, setDashboardTitle] = useState("");
  const [dashboardUid, setDashboardUid] = useState("");
  const [csvFile, setCsvFile] = useState(null);
  const [features, setFeatures] = useState([]);
  const [metadata, setMetadata] = useState([]);
  const [csvUploaded, setCsvUploaded] = useState(false);
  const [page, setPage] = useState(1);
  const [sentence, setSentence] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [currentQueryIndex, setCurrentQueryIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  const chatInputRef = useRef(null);

  useEffect(() => {
    if (chatInputRef.current) {
      chatInputRef.current.focus();
    }
  }, [currentQueryIndex]);

  const createDashboard = async () => {
    try {
      const response = await axios.post(
        "/api/dashboards/db",
        {
          dashboard: {
            id: null,
            uid: null,
            title: dashboardTitle,
            tags: ["templated"],
            timezone: "browser",
            schemaVersion: 16,
            refresh: "25s",
          },
          message: "Made changes to xyz",
          overwrite: false,
        },
        {
          headers: {
            Authorization:
              "Bearer {Grafana Service Account Key}",
            "Content-Type": "application/json",
          },
        }
      );
      setDashboardUid(response.data.uid);
    } catch (error) {
      console.error("Error creating dashboard:", error);
    }
  };

  const handleCsvFileChange = async (e) => {
    setCsvFile(e.target.files[0]);
    const formData = new FormData();
    formData.append("file", e.target.files[0]);

    setLoading(true); // Show loading indicator

    const response = await axios.post(
      "http://localhost:8000/get_csv_schema/",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
     
    formData.append("CsvSchema", response.data.features);
    setFeatures(response.data.features);
    const featuresArray = response.data.features.map((feature) => ({
      feature_name: feature,
    }));

    console.log("Features: ", response.data.features);

    const aiResponse = await axios.post(
      "http://localhost:8000/get_feature_metadata/",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    setLoading(false); // Hide loading indicator

    console.log("aiResponse: ", aiResponse.data);
  
    const featureMetadata = aiResponse.data.metadata;
    console.log("AIResponseFeatures: ", aiResponse.data.metadata);
    setMetadata(featureMetadata);
    setCsvUploaded(true);
  };

  const handleMetadataChange = (index, key, value) => {
    const newMetadata = [...metadata];
    newMetadata[index][key] = value;
    setMetadata(newMetadata);
  };

  const handleSentenceChange = (e) => {
    setSentence(e.target.value);
  };

  const startNewQuery = () => {
    setCurrentQueryIndex(null);
    setSentence("");
  };

  const handleQueryClick = (index) => {
    setCurrentQueryIndex(index);
    setSentence(chatHistory[index].sentence);
  };

  const createPanel = async () => {
    try {
      const formData = new FormData();
      formData.append("file", csvFile);
      formData.append("sentence", sentence);
      formData.append("metadata", JSON.stringify(metadata));  
      formData.append("CsvSchema", features);
      const response = await axios.post(
        "http://localhost:8000/generate_sql/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const {
        sql_query: sqlQuery,
        response_type: responseType,
        graph_type: graphType,
        text_response: textResponse,
      } = response.data;

      if (responseType === "text") {
        setChatHistory([...chatHistory, { sentence, textResponse }]);
      } else {
        const existingDashboardResponse = await axios.get(
          `/api/dashboards/uid/${dashboardUid}`,
          {
            headers: {
              Authorization:
                "Bearer {Grafana Service Account Key}",
              "Content-Type": "application/json",
            },
          }
        );

        const existingDashboard = existingDashboardResponse.data.dashboard;

        if (!existingDashboard.panels) {
          existingDashboard.panels = [];
        }
        console.log("GraphType: ", graphType);
        const newPanel = {
          type: graphType !== null ? graphType : "table",
          title: graphType !== null ? graphType : "Table",
          gridPos: { h: 8, w: 12, x: 0, y: 0 },
          datasource: "grafana-postgresql-datasource-11",
          targets: [{ rawSql: sqlQuery, format: "table", refId: "A" }],
          ...(graphType !== null && {
            xaxis: { mode: "time" },
            yaxes: [{ format: "short" }, { format: "short" }],
            options: {
              reduceOptions: {
                fields: "",
                values: true,
              },
              tooltip: {
                mode: "multi",
              },
            },
          }),
        };

        existingDashboard.panels.push(newPanel);

        await axios.post(
          "/api/dashboards/db",
          {
            dashboard: existingDashboard,
            message: "Added sample chart",
            overwrite: true,
          },
          {
            headers: {
              Authorization:
                "Bearer {Grafana Service Account Key}",
              "Content-Type": "application/json",
            },
          }
        );

        const newPanelIndex = existingDashboard.panels.length;
        const panelUrl = `http://localhost/d/${dashboardUid}?orgId=1&viewPanel=${newPanelIndex}&kiosk`;

        setChatHistory([...chatHistory, { sentence, panelUrl }]);
      }
      setSentence("");
      setCurrentQueryIndex(chatHistory.length); // Reset to show the latest query
    } catch (error) {
      console.error("Error creating panel:", error);
    }
  };

  const saveMetadataToFile = () => {
    const metadataString = JSON.stringify(metadata, null, 2);
    const blob = new Blob([metadataString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "metadata.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="dashboard-creator">
      {page === 1 && (
      <div className="dashboard-left">
        <h1>Dashboard</h1>
        <div className="input-group">
          <label htmlFor="dashboardTitle">Dashboard Title: </label>
          <input
            type="text"
            id="dashboardTitle"
            value={dashboardTitle}
            onChange={(e) => setDashboardTitle(e.target.value)}
            style={{ fontSize: "16px" }}
          />
          <button className="btn-primary" onClick={createDashboard}>
            Create Dashboard
          </button>
        </div>
        {dashboardUid && (
          <div>
            <div className="input-group">
              <br />
              <label htmlFor="csvFile">Upload CSV File: </label>
              <input type="file" id="csvFile" onChange={handleCsvFileChange} />
            </div>
            <br />
            {loading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>Fetching metadata...</p>
              </div>
            )}
            {csvUploaded && (
              <div className="metadata-section">
                <h3>CSV Features Metadata</h3>
                {metadata.map((feature, index) => (
                  <div key={index} className="metadata-item">
                    <label>Name: </label>
                    <input
                      type="text"
                      value={feature.name}
                      readOnly
                      style={{ marginBottom: "5px", marginRight:"10px" }} 
                    />
                    <label>Description: </label>
                    <input
                      type="text"
                      value={feature.description}
                      onChange={(e) =>
                        handleMetadataChange(index, "description", e.target.value)
                      }
                      style={{ marginBottom: "5px", marginRight:"10px" }} 
                    />
                    <label>Data Type: </label>
                    <input
                      type="text"
                      value={feature.dataType}
                      onChange={(e) =>
                        handleMetadataChange(index, "dataType", e.target.value)
                      }
                      style={{ marginBottom: "5px", marginRight:"10px" }}
                    />
                     <label>PreferredVisualizationType: </label>
                    <input
                      type="text"
                      value={feature.preferredVisualizationType}
                      onChange={(e) =>
                        handleMetadataChange(index, "preferredVisualizationType", e.target.value)
                      }
                      style={{ marginBottom: "5px" }}
                    />
                  </div>
                ))}
                <button className="btn-primary" onClick={saveMetadataToFile}>
                  Save Metadata
                </button>
                <button
                  className="btn-primary"
                  onClick={() => setPage(2)}
                  style={{ marginLeft: "10px" }}
                >
                  Chat
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      )}
      {page === 2 && (
      <div className="dashboard-right">
      {/* Remove the heading "Dashboard" */}
      <div className="chat-history">
        {/* Remove the heading "Chat History" */}
        <ul>
          {chatHistory.map((chat, index) => (
            <li
              key={index}
              onClick={() => handleQueryClick(index)}
              className={currentQueryIndex === index ? "active-query" : ""}
            >
              <strong>Query:</strong> {chat.sentence}
              {chat.textResponse && (
                <>
                  <br />
                  <strong>Response:</strong> {chat.textResponse}
                </>
              )}
              {chat.panelUrl && (
                <>
                  <iframe
                      title="Chart"
                      width="100%"
                      height="350px"
                      src={chat.panelUrl}
                      frameBorder="0"
                      allowFullScreen
                    ></iframe>
                </>
              )}
            </li>
          ))}
        </ul>
      </div>
      <div className="input-group fixed-input">
        <input
          type="text"
          id="chatInput"
          value={sentence}
          onChange={handleSentenceChange}
          ref={chatInputRef}
          style={{ fontSize: "16px",width:"75%", borderRadius:"5px",height:"90%",marginRight:"40px" }}
          placeholder="Type your query here...."
        />
        <button className="btn-primary" onClick={createPanel}>
          Send Query
        </button>
        <button
          className="btn-primary"
          onClick={() => setPage(1)}
          style={{ marginLeft: "10px" }}
        >
          Dashboard
        </button>
      </div>
    </div>
  )}
    </div>
  );
};

export default DashboardCreator;
